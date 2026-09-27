#!/usr/bin/env Rscript
# Read-only tracing of official function arguments; no argument or body is changed.
self <- sub('^--file=','',commandArgs()[grep('^--file=',commandArgs())][1])
root <- dirname(normalizePath(self))
.libPaths(c(file.path(root,'Rlibrary'),file.path(dirname(root),'honestdid_extension','Rlibrary'),file.path(dirname(root),'honestdid','Rlibrary'),.libPaths()))
library(HonestDiD)
seed_audit <- list(); model_label <- NA_character_
trace('.compute_least_favorable_cv',where=asNamespace('HonestDiD'),print=FALSE,
 tracer=quote({
    seed_audit[[length(seed_audit)+1L]] <<- data.frame(model=model_label,
      requested_outer_seed=20260927,effective_internal_seed=seed,simulations=sims)
 }))
for(model_label in c('unadjusted','adjusted')) {
 data_root <- if(model_label=='unadjusted') root else {
   candidates <- c(file.path(dirname(root),'honestdid'),file.path(dirname(root),'honestdid_extension'))
   candidates[dir.exists(candidates)][1]
 }
 b <- read.csv(file.path(data_root,'event_coefficients_full.csv'))$beta
 s <- as.matrix(read.csv(file.path(data_root,'event_covariance.csv'),row.names=1))
 z <- HonestDiD::computeConditionalCS_DeltaRM(betahat=b,sigma=s,numPrePeriods=11,
       numPostPeriods=12,l_vec=c(rep(0,3),rep(1/9,9)),Mbar=0,alpha=.05,
       hybrid_flag='LF',hybrid_kappa=.005,returnLength=FALSE,
       gridPoints=1,grid.lb=0,grid.ub=0,seed=20260927)
 stopifnot(z$accept==0)
}
untrace('.compute_least_favorable_cv',where=asNamespace('HonestDiD'))
audit <- do.call(rbind,seed_audit)
stopifnot(nrow(audit)==44,all(audit$effective_internal_seed==0),all(audit$simulations==1000))
write.csv(audit,file.path(root,'internal_seed_runtime_audit.csv'),row.names=FALSE)
print(aggregate(cbind(effective_internal_seed,simulations)~model,audit,unique))
