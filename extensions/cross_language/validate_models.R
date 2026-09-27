#!/usr/bin/env Rscript
# Independent ordinary least squares with explicit fixed-effect indicators.
# Route-clustered CR1 covariance is computed directly, without Python code.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=2) stop('Usage: Rscript validate_models.R REPOSITORY_DIRECTORY OUTPUT_DIRECTORY')
repo <- normalizePath(args[1],mustWork=TRUE)
out <- args[2];dir.create(out,recursive=TRUE,showWarnings=FALSE)
features <- read.csv(file.path(repo,'results','route_features.csv'),stringsAsFactors=FALSE,na.strings=c('','NA'))
legacy <- read.csv(file.path(repo,'results','panel_legacy_valid.csv'),stringsAsFactors=FALSE)
expanded <- read.csv(file.path(repo,'results','panel_all_unexposed.csv'),stringsAsFactors=FALSE)
prepare <- function(d) {
  d <- d[order(d$route,d$t),]
  d$did <- as.numeric(d$treated==1 & d$t>=16)
  d$wn_present <- as.integer(features$wn[match(d$route,features$route)]>0)
  stopifnot(!anyNA(d$wn_present), all(is.finite(d$lnfare)))
  d
}
legacy<-prepare(legacy);expanded<-prepare(expanded)
models<-list(
  list(name='same_sample_unadjusted',data=legacy,controls=''),
  list(name='distance_quarter',data=legacy,controls='+ factor(distance_bin):factor(t)'),
  list(name='distance_and_composition_quarter',data=legacy,controls='+ factor(distance_bin):factor(t) + factor(share_bin):factor(t)'),
  list(name='all_controls_adjusted',data=expanded,controls='+ factor(distance_bin):factor(t) + factor(share_bin):factor(t)'),
  list(name='legacy_adjusted_wn_present',data=legacy,controls='+ factor(distance_bin):factor(t) + factor(share_bin):factor(t) + factor(wn_present):factor(t)'),
  list(name='expanded_adjusted_wn_present',data=expanded,controls='+ factor(distance_bin):factor(t) + factor(share_bin):factor(t) + factor(wn_present):factor(t)')
)
rows<-list()
for (spec in models) {
  cat('Estimating',spec$name,'\n');flush.console()
  formula<-as.formula(paste('lnfare ~ did + factor(route) + factor(t)',spec$controls))
  fit<-lm(formula,data=spec$data,x=TRUE,y=TRUE,tol=1e-10)
  # Keep the independent columns selected by R's QR, including the did column.
  retained<-fit$qr$pivot[seq_len(fit$rank)]
  X<-fit$x[,retained,drop=FALSE];u<-residuals(fit)
  j<-match('did',colnames(X));stopifnot(!is.na(j),!is.na(coef(fit)['did']))
  bread<-solve(crossprod(X))
  scores<-rowsum(X*as.numeric(u),spec$data$route,reorder=FALSE)
  N<-nrow(X);G<-nrow(scores);K<-fit$rank
  correction<-G/(G-1)*(N-1)/(N-K)
  # The target variance computed from cluster scores equals the appropriate
  # diagonal element of (X'X)^(-1) S'S (X'X)^(-1), times CR1.
  v<-bread[,j];se<-sqrt(sum((scores%*%v)^2)*correction)
  beta<-unname(coef(fit)['did']);critical<-qt(.975,G-1)
  rows[[length(rows)+1]]<-data.frame(model=spec$name,language='R',N=N,routes=G,rank=K,df_resid=N-K,b=beta,se=se,lo=beta-critical*se,hi=beta+critical*se,p=2*pt(-abs(beta/se),df=G-1),pct=100*expm1(beta),pct_lo=100*expm1(beta-critical*se),pct_hi=100*expm1(beta+critical*se),stringsAsFactors=FALSE)
  # Save a version of the actual specification for inspection.
  cat(spec$name,'N',N,'G',G,'rank',K,'beta',sprintf('%.16g',beta),'se',sprintf('%.16g',se),'\n')
}
result<-do.call(rbind,rows)
write.csv(result,file.path(out,'r_model_results.csv'),row.names=FALSE,na='')
writeLines(c(R.version.string,paste('Platform:',R.version$platform),'No contributed packages used. Explicit fixed effects and independently computed route-clustered CR1 standard errors.',capture.output(sessionInfo())),file.path(out,'r_session_info.txt'))
print(result,row.names=FALSE,digits=12)
