setwd("/home/stefano/SATD-Analysis/CommunitySmell/dataset-finale/dataset-FINALI-communitysmells/")

library(lme4)
library(xtable)
library(Hmisc)

t<-read.csv("totale-CS_dataset.csv")

attach(t)

normalized<-function(y) {

  x<-y[!is.na(y)]

  x<-(x - min(x)) / (max(x) - min(x))

  y[!is.na(y)]<-x

  return(y)
}



SATD=CommentType=="SATD"

#indepvar=c("NLOC","Complexity","X.Parameters","NLOC_slope","Complexity_slope","pmd_warnings_numbers","checkstyle_warnings_numbers","missing_links","org_silo","radio_silence")

#redunvar=c("NLOC","Complexity","X.Parameters","NLOC_slope","pmd_warnings_numbers","checkstyle_warnings_numbers","missing_links","org_silo","radio_silence")

indepvar=c("missing_links","org_silo","radio_silence")

redunvar=c("missing_links","org_silo","radio_silence")



#redunf=paste("SATD",paste(redunvar,collapse="+"),sep="~")
redunf=paste("SATD",paste(redunvar,collapse="+"),sep="~")
toRemove<-redun(formula(redunf),r2=0.64,nk=10)

allIndep=t[,indepvar]

prunedVar=allIndep[, !(colnames(allIndep) %in% toRemove$Out)]

normalizedVar=data.frame(apply(prunedVar,2,normalized))

overall=cbind(normalizedVar,Project)
attach(overall)


random="+(1|Project)"
indep=paste(colnames(normalizedVar),collapse="+")
rightside=paste(indep,random,sep="")
fm=paste("SATD",rightside,sep="~")
print(fm)

model=glmer(formula(fm),family="binomial",control=glmerControl(optimizer="nloptwrap",calc.derivs=FALSE,optCtrl=list(maxfun=2e6)))

summary(model)

xtable(summary(model)$coefficients,digits=4)






#####################################################

t<-read.csv("totale-CS_dataset.csv")

attach(t)

normalized<-function(y) {

  x<-y[!is.na(y)]

  x<-(x - min(x)) / (max(x) - min(x))

  y[!is.na(y)]<-x

  return(y)
}



SATD=CommentType=="SATD"

redunvar=c("missing_links","org_silo","radio_silence")
allIndep=t[redunvar]

prunedVar=allIndep[colnames(allIndep)]

normalizedVar=data.frame(apply(prunedVar,2,normalized))

overall=cbind(normalizedVar,Project)
attach(overall)


random="+(1|Project)"
indep=paste(colnames(normalizedVar),collapse="+")
rightside=paste(indep,random,sep="")
fm=paste("SATD",rightside,sep="~")
print(fm)

model=glmer(formula(fm),family="binomial",control=glmerControl(optimizer="nloptwrap",calc.derivs=FALSE,optCtrl=list(maxfun=2e6)))

summary(model)

xtable(summary(model)$coefficients,digits=4)






