
url.base="http://dathomir.lan/zartog/tmp7"
url.skin=paste(url.base,"dépeçage-Balangar.csv",sep="/")
url.tous=paste(url.base,"tous-les-dépeçages-de-Balangar.csv",sep="/")

skin <- read.csv(url(url.skin),row.names = 1)
summary(skin)
s2 <- subset(skin,skin$Don.entrant>100)
s3 <-s2[order(s2$Don.entrant,decreasing = TRUE),]
s2 <- subset(skin,skin$mes.parts>0)
s2$ratio <- format(s2$mes.parts / s2$combien, digits=1,nsmall=2)
s4 <-s2[order(s2$ratio,decreasing = TRUE),]

