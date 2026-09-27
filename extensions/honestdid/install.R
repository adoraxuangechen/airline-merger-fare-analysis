#!/usr/bin/env Rscript
# Install official HonestDiD at a fixed commit into an extension-local library.
# No global R packages are installed or changed. Network access and git required.
self <- sub('^--file=', '', commandArgs()[grep('^--file=',commandArgs())][1])
root <- dirname(normalizePath(self))
lib <- file.path(root,'Rlibrary')
dir.create(lib,recursive=TRUE,showWarnings=FALSE)
.libPaths(c(lib,.libPaths()))
commit <- '6813f02ed38f0b63bdca6915604b2eac90491303'
source_dir <- file.path(root,'.cache',paste0('HonestDiD-',commit))
if(!dir.exists(file.path(source_dir,'.git'))) {
 dir.create(source_dir,recursive=TRUE,showWarnings=FALSE)
 stopifnot(system2('git',c('init',shQuote(source_dir)))==0)
 stopifnot(system2('git',c('-C',shQuote(source_dir),'remote','add','origin',
      'https://github.com/asheshrambachan/HonestDiD.git'))==0)
}
stopifnot(system2('git',c('-C',shQuote(source_dir),'fetch','--depth','1','origin',commit))==0)
stopifnot(system2('git',c('-C',shQuote(source_dir),'checkout','--detach',commit))==0)
actual_commit <- system2('git',c('-C',shQuote(source_dir),'rev-parse','HEAD'),stdout=TRUE)
stopifnot(identical(actual_commit,commit))
desc <- read.dcf(file.path(source_dir,'DESCRIPTION'))
tokens <- trimws(strsplit(desc[1,'Imports'], ',')[[1]])
p <- trimws(gsub('\\s*\\([^)]*\\)', '', tokens))
needs_install <- vapply(seq_along(p), function(i) {
 if(!length(find.package(p[i],quiet=TRUE))) return(TRUE)
 if(grepl('>=',tokens[i],fixed=TRUE)) {
  minimum <- trimws(sub('.*>= *([^)]*)\\).*', '\\1', tokens[i]))
  return(packageVersion(p[i]) < package_version(minimum))
 }
 FALSE
}, logical(1))
if(any(needs_install)) install.packages(p[needs_install],repos='https://cloud.r-project.org',lib=lib)
# R CMD INSTALL also validates all declared minimum-version requirements.
install.packages(source_dir,repos=NULL,type='source',lib=lib)
stopifnot(requireNamespace('HonestDiD',quietly=TRUE),
          as.character(packageVersion('HonestDiD'))=='0.2.8')
versions <- installed.packages()[,c('Package','Version','Built'),drop=FALSE]
write.csv(versions,file.path(root,'R_dependency_versions.csv'),row.names=FALSE)
writeLines(c(commit,paste0('Version: ',desc[1,'Version']),
             'Source: https://github.com/asheshrambachan/HonestDiD'),
           file.path(root,'official_source_version.txt'))
