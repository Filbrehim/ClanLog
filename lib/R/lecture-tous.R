
library(dplyr)

url.base="http://dathomir.lan/Puddleby"
url.skin=paste(url.base,"dépeçage-Balangar.csv",sep="/")
url.tous=paste(url.base,"tous-les-dépeçages-de-Balangar.csv",sep="/")

étude <- read.csv(url(url.tous))
summary(étude)

# original
consolidé = étude |>
  group_by(across(all_of(c("qui","quoi"))), .add = TRUE) |>
  summarize(combien=n(),
            moyenne=format(mean(vaut),digits=1,nsmall=2),médianne=median(vaut),
            total=sum(vaut),
            min=min(vaut),max=max(vaut),
            .groups="rowwise")

analyse <- function(rechercher) {
  print(paste("on recherche",rechercher))

e2  <- étude |>
  filter(quoi == rechercher ) |>
  group_by(across(all_of(c("qui","quoi"))), .add = TRUE) |>
  summarize(combien=n(),
            médianne=median(vaut),
            .groups="rowwise")

  e3  <- subset(e2,(e2$quoi == quoi)&(e2$combien>1))
  moi <- filter(e3, substr(qui,1,3) == "moi")
  e4  <- e3[order(e3$médianne, decreasing = TRUE),]
  plot(x=e4$combien,y=e4$médianne,xlab="combien",ylab="médianne",
       main=rechercher,
       sub=paste("le total est de",sum(e3$combien),"mesures pour",nrow(e3),"éléments.")) 
  if ( nrow(moi)> 0 ) {
      par(new = TRUE)
      text(x=moi$combien,y=moi$médianne,label=moi$qui)
  }
}

analyse_total <- function(rechercher) {
  print(paste("on recherche",rechercher))
  
  e2 = étude |>
    filter(quoi == rechercher) |>
    group_by(across(all_of(c("qui","quoi"))), .add = TRUE) |>
    summarize(combien=n(),
              total=sum(vaut),
              .groups="rowwise")
  
  e3 <- subset(e2,e2$quoi == quoi)
  moi = filter(e3, substr(qui,1,3) == "moi")
  e4 <- e3[order(e3$total, decreasing = TRUE),]
  plot(x=e4$combien,y=e4$total,xlab="combien",ylab="total",
       main=rechercher,
       sub=paste("le total est de",sum(e3$combien),"mesures pour",nrow(e3),"éléments.")) 
  
  if ( nrow(moi)> 0 ) {
    par(new = TRUE)
    text(x=moi$combien,y=moi$total,label=moi$qui)
  }
}

analyse("Utsanna Tawny Yorilla")
analyse_total("Utsanna Tawny Yorilla")

analyse("Lowland Panther")
analyse("Shadowcat Warqueen")
analyse("Tawny Yorilla")

analyse("Dark Recluse")
analyse_total("Dark Recluse")