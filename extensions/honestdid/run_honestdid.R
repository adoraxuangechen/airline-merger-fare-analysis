#!/usr/bin/env Rscript
# Official HonestDiD sensitivity, fixed quarter calendar and target weights.
args <- commandArgs(trailingOnly=TRUE)
mode <- if(length(args)) args[1] else 'pilot'
self <- sub('^--file=', '', commandArgs()[grep('^--file=',commandArgs())][1])
root <- dirname(normalizePath(self))
.libPaths(c(file.path(root,'Rlibrary'),.libPaths()))
library(HonestDiD)
options(warn=1)
coef <- read.csv(file.path(root,'event_coefficients_full.csv'))
sigma <- as.matrix(read.csv(file.path(root,'event_covariance.csv'),row.names=1,check.names=FALSE))
beta <- coef$beta
stopifnot(length(beta)==23, min(eigen(sigma,symmetric=TRUE,only.values=TRUE)$values)>0,
          identical(rownames(sigma),coef$term), identical(colnames(sigma),coef$term))
lvec <- c(rep(0,3),rep(1/9,9))
common <- list(betahat=beta,sigma=sigma,numPrePeriods=11,numPostPeriods=12,l_vec=lvec,alpha=.05)
original <- do.call(HonestDiD::constructOriginalCS,common)
write.csv(original,file.path(root,'original_confidence_set.csv'),row.names=FALSE)
# trace saves the official underlying test-inversion acceptance grid unchanged;
# this permits auditing truncation and disconnected acceptance sets.
CAPTURE_DIR <- file.path(root,paste0(mode,'_grids'))
dir.create(CAPTURE_DIR,showWarnings=FALSE)
trace('computeConditionalCS_DeltaRM',where=asNamespace('HonestDiD'),print=FALSE,
      exit=quote({write.csv(returnValue(),file.path(get('CAPTURE_DIR',envir=.GlobalEnv),paste0('M',Mbar,'.csv')),row.names=FALSE)}))
if(mode=='pilot') { gridpoints <- 41L; lb <- -1; ub <- 1; mvec <- c(0,.5,1,2) }
if(mode=='full') { gridpoints <- 1001L; lb <- -2.5; ub <- 2.5; mvec <- c(0,.5,1,2) }
if(startsWith(mode,'single')) {
 mval <- as.numeric(args[2]); mvec <- mval
 ranges <- list('0'=c(-.12,.03), '0.5'=c(-.55,.5), '1'=c(-1.1,1.05), '2'=c(-2.2,2.15))
 endpoints <- ranges[[as.character(mval)]]
 lb <- endpoints[1];ub <- endpoints[2]
 gridpoints <- if(mval==0) 1001L else if(mval==.5) 1001L else if(mval==1) 431L else 871L
}
if(mode=='widepilot') { gridpoints <- 61L; lb <- -2.2; ub <- 2.15; mvec <- 2 }
start <- Sys.time()
result <- do.call(HonestDiD::createSensitivityResults_relativeMagnitudes,
     c(common,list(Mbarvec=mvec,method='C-LF',gridPoints=gridpoints,
                   grid.lb=lb,grid.ub=ub,parallel=FALSE,seed=20260927)))
write.csv(result,file.path(root,paste0(mode,'_sensitivity.csv')),row.names=FALSE)
saveRDS(list(result=result,original=original,beta=beta,sigma=sigma,l_vec=lvec,
             gridPoints=gridpoints,grid.lb=lb,grid.ub=ub,Mbarvec=mvec,
             seed=20260927,start=start,end=Sys.time(),sessionInfo=sessionInfo()),
        file.path(root,paste0(mode,'_sensitivity.rds')))
writeLines(capture.output(sessionInfo()),file.path(root,'R_sessionInfo.txt'))
print(result); print(Sys.time()-start)
untrace('computeConditionalCS_DeltaRM',where=asNamespace('HonestDiD'))
versions <- installed.packages()[,c('Package','Version','Built'),drop=FALSE]
write.csv(versions,file.path(root,'R_dependency_versions.csv'),row.names=FALSE)
