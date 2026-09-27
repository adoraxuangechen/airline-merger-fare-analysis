#!/usr/bin/env Rscript
# Verify direct zero tests against full official confidence-set inversions.
self <- sub('^--file=','',commandArgs()[grep('^--file=',commandArgs())][1])
root <- dirname(normalizePath(self));args <- commandArgs(trailingOnly=TRUE)
lib_candidates <- c(file.path(root,'Rlibrary'),file.path(dirname(root),'honestdid_extension','Rlibrary'),file.path(dirname(root),'honestdid','Rlibrary'))
.libPaths(c(lib_candidates[dir.exists(lib_candidates)],.libPaths()))
library(HonestDiD)
output_dir <- root;weights <- c(rep(0,3),rep(1/9,9))
if(length(args)>=2 && args[1]=='--weights') {
 weights <- read.csv(args[2])$weight;stopifnot(length(weights)==12)
 output_dir <- file.path(root,'pooled_associated');args <- args[-c(1,2)]
}
mvals <- as.numeric(args);stopifnot(length(mvals)>0,all(is.finite(mvals)))
b <- read.csv(file.path(root,'event_coefficients_full.csv'))$beta
s <- as.matrix(read.csv(file.path(root,'event_covariance.csv'),row.names=1))
CAPTURE_DIR <- file.path(output_dir,'full_grid_validation');dir.create(CAPTURE_DIR,showWarnings=FALSE)
trace('computeConditionalCS_DeltaRM',where=asNamespace('HonestDiD'),print=FALSE,
  exit=quote({write.csv(returnValue(),file.path(get('CAPTURE_DIR',envir=.GlobalEnv),paste0('M',Mbar,'.csv')),row.names=FALSE)}))
# This explicit grid contains theta=0; it is sufficiently wide for these local M values.
result <- HonestDiD::createSensitivityResults_relativeMagnitudes(betahat=b,sigma=s,
 numPrePeriods=11,numPostPeriods=12,l_vec=weights,Mbarvec=mvals,method='C-LF',
 alpha=.05,grid.lb=-.25,grid.ub=.1,gridPoints=351,parallel=FALSE,seed=20260927)
untrace('computeConditionalCS_DeltaRM',where=asNamespace('HonestDiD'))
checks <- lapply(mvals,function(m) {
 z <- read.csv(file.path(CAPTURE_DIR,paste0('M',m,'.csv')))
 index <- which.min(abs(z$grid));stopifnot(abs(z$grid[index])<1e-14,
  z$accept[1]==0,z$accept[nrow(z)]==0)
 data.frame(Mbar=m,zero_accepted=z$accept[index],closest_theta=z$grid[index],
  grid_lower=z$grid[1],grid_upper=tail(z$grid,1),grid_step=max(diff(z$grid)),
  components=sum(diff(c(0,z$accept))==1),endpoint_truncation=FALSE)
})
write.csv(result,file.path(CAPTURE_DIR,'confidence_sets.csv'),row.names=FALSE)
write.csv(do.call(rbind,checks),file.path(CAPTURE_DIR,'zero_membership_checks.csv'),row.names=FALSE)
saveRDS(list(result=result,checks=checks,weights=weights,seed_argument=20260927,
 effective_internal_lf_seed=0,internal_simulations=1000),file.path(CAPTURE_DIR,'validation.rds'))
print(result);print(do.call(rbind,checks))
