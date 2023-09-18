################# 서울시 지역구별 투기과열지구 지정 확률 추정 ##################

setwd("C:\\Users\\soyou\\Dropbox\\대체보고서")
library(readxl)
df <- read_excel("연도별_투기과열지구여부.xlsx", sheet = "Sheet1")
add <- colnames(df)

final_posmean <- c()
for (k in 1:length(add)) {
  data <- df[[add[k]]]
  alpha <- 1
  beta <- 1
  pos_mean <- c()
  for (j in 1:(length(data)-1)) {
    init_dt <- data[1:j+1]
    y <- sum(init_dt)
    n <- length(init_dt)
    pos_mean[j] <- (y+alpha) / (alpha + beta + n)
    alpha <- y+alpha
    beta <- n-y+beta
  }
  final_posmean[k] <- pos_mean[20] 
}
final_posmean
posmean_list <- data.frame(add, final_posmean)
write.csv(posmean_list, '투기과열지구확률.csv', row.names = F,fileEncoding = 'cp949')

################### 강남구 posterior mean 추정(예시) ##########################
data <- c(1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1)
alpha <- 1
beta <- 1
pos_mean <- c()
density_list <- list()
for (j in 1:(length(data)-1)) {
  init_dt <- data[1:j+1]
  y <- sum(init_dt)
  n <- length(init_dt)
  pos_mean[j] <- (y+alpha) / (alpha + beta + n)
  
  x <- seq(0,1, 0.001)
  density <- vector("double")
  for (i in seq_along(x)) {
    density[i] <- dbeta(x[i], y+alpha, n-y+beta)
  }
  density_list[[j]] <- density
  alpha <- y+alpha
  beta <- n-y+beta
}

n_th <- seq(1, (length(density_list)-1),3)
plot(x, density_list[[1]], type= "l", xlim = c(0.4, 1), ylim = c(0,20),
     xlab = 'p', ylab = "", yaxt = "n")
for (i in n_th) {
  lines(x, density_list[[i+1]])
}
abline(v = pos_mean[20], col = 'red')
text(x = 0.62, y = 19,
     paste("Posterior mean =", round(pos_mean[20],2)), cex = 0.8, adj = c(1,0),
     col = 'red')