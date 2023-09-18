
############### Bayesian Cost-Effectiveness Analysis #############
############### Gibs Sampling by JAGS ###############

library(tidyverse)
library(R2jags)

# Load your data

# Data
df <- read.csv("C:\\Users\\soyou\\Dropbox\\대체보고서\\분양 데이터\\merge\\seoul_score_cost_0913.csv")
colnames(df)
df$cost_log <- log(df$total_cost)
head(df)

# score와 cost 데이터만 선택
df_1 <- df[df$region == 0, c("q_score", "cost_log")] # 비강남
df_2 <- df[df$region == 1, c("q_score", "cost_log")] #강남4구

# 데이터 프레임을 matrix 형태로 변환하기 (그래야 피팅 가능)
y_data1 <- cbind(df_1$q_score, df_1$cost_log)
y_data2 <- cbind(df_2$q_score, df_2$cost_log)

data <- list(
  # Real Data
  y1 = y_data1,
  y2 = y_data2,
  # Number of Observation
  n1 = nrow(y_data1),
  n2 = nrow(y_data2),
  # Initial values for mu and V and A
  mu1 = c(1, 1),
  mu2 = c(10, 10),
  prec1 = solve(diag(c(10000,10000))),
  prec2 = solve(diag(c(10000,10000))),
  A1 = diag(c(1,1)),
  A2 = diag(c(1,1)),
  f1 = 4,
  f2 = 4
)

modelString = " model {
  for (i in 1:n1) {
    y1[i, 1:2] ~ dmnorm(alpha1[], phi1[,])
  }
  for (j in 1:n2) {
    y2[j, 1:2] ~ dmnorm(alpha2[], phi2[,])
  }
  alpha1[1:2] ~ dmnorm(mu1[], prec1[,])
  alpha2[1:2] ~ dmnorm(mu2[], prec2[,])
  phi1[1:2,1:2] ~ dwish(A1[,], f1)
  phi2[1:2,1:2] ~ dwish(A2[,], f2)
} "

setwd("C:/Users/soyou/Desktop/JAGS")
writeLines(modelString, con = "TEMPmodel.text")

# Specify the path to your JAGS model file
model_file <- "C:/Users/soyou/Desktop/JAGS/TEMPmodel.text"

# Specify initial values for alpha and sigma
# MLE of y~N(alpha, V)
random_mle <- function(y,n) {
  random_row_index <- sample(nrow(y), n,replace = TRUE)
  random_row <- y[random_row_index, ]
  alpha_mle <- colMeans(random_row)
  init_mat <- diag(c(0,0))
  for (i in 1:nrow(random_row)) {
    u <- random_row[i,] - alpha_mle
    sigma_mle <- crossprod(t(u), u)
    init_mat <- init_mat + sigma_mle
  }
  sigma_mle <- init_mat / n
  
  return(list(alpha_mle, sigma_mle))
}

# 각 y 데이터 그룹의 sample MLE 구하기 (sample은 전체 N수의 1/3)
random_mle(y_data1, nrow(y_data1)/3)
random_mle(y_data2, nrow(y_data2)/3)

inits1 <- list(alpha1 = c(33.90749, 10.56566),
               alpha2 = c(50.17689, 11.03922),
               phi1 = solve(matrix(c(185.378254,4.411747,4.411747,0.1643575), nrow=2)),
               phi2 = solve(matrix(c(260.363976,6.205893,6.205893,0.2413291), nrow=2)))
inits2 <- list(alpha1 = c(34.03678, 10.61426),
               alpha2 = c(50.62713, 11.27473),
               phi1 = solve(matrix(c(103.499981,2.059075,2.059075,0.09591287), nrow=2)),
               phi2 = solve(matrix(c(815.45245,25.79769,25.79769,0.9285521), nrow=2)))
inits3 <- list(alpha1 = c(27.36051, 4.7599254),
               alpha2 = c(55.82137, 11.42899),
               phi1 = solve(matrix(c(185.395793,4.759925,4.759925,0.2451007), nrow=2)),
               phi2 = solve(matrix(c(382.43427,11.39266,11.39266,0.4269222), nrow=2)))
inits <- list(inits1, inits2, inits3)

# Run MCMC simulation
jagsModel <- jags.model(data = data,file = textConnection(modelString), inits = inits,
                        n.chains = 3,n.adapt = 500)
update(jagsModel, n.iter = 500)
codaSamples = coda.samples(jagsModel, variable.names = c("alpha1", "alpha2", "phi1", "phi2"),
                           n.iter = 4000)

# Convergence Diagnosis
source("C:/Users/soyou/Desktop/JAGS/DBDA2E-utilities.R")
diagMCMC(codaObject = codaSamples, parName = "phi2[2,2]")

# 생성된 MCMC 샘플 확인
codaSamples

# MCMC Samples summary 저장
summary1 <- data.frame(summary(codaSamples)[1])
summary2 <- data.frame(summary(codaSamples)[2])
total_sum <- cbind(summary1, summary2)
setwd('C:\\Users\\soyou\\Dropbox\\대체보고서\\MCMC')
write.csv(total_sum, 'MCMC_summary_0913.csv')


# MCMC 샘플 데이터 프레임 형태로 저장
empty <- data.frame()
for (i in 1:3) {
  sample <- as.data.frame(as.mcmc(codaSamples[[i]]))
  empty <- rbind(empty, sample)
}
# 저장하기
write.csv(empty, "C:/Users/soyou/Dropbox/대체보고서/MCMC/MCMC_samples_0913.csv", row.names = F)

# 파일 불러오기
library(tidyverse)
library(data.table)
sample <- fread("C:/Users/soyou/Dropbox/대체보고서/MCMC/MCMC_samples_0913.csv")
head(sample)

# 히스토그램 그리기
hist(sample$`alpha1[1]`, probability = T, breaks = 100)
hist(sample$`alpha1[2]`, probability = T, breaks = 100)
hist(sample$`alpha2[1]`, probability = T, breaks = 100)
hist(sample$`alpha2[2]`, probability = T, breaks = 100)

# 컬럼 이름 바꾸기
colnames(sample) <- c('g0_mean_e', 'g0_mean_logc', 'g1_mean_e', 'g1_mean_logc',
                      'g0_sig11', 'g0_sig21', 'g0_sig12', 'g0_sig22',
                      'g1_sig11', 'g1_sig21', 'g1_sig12', 'g1_sig22')


# 로그 변환 된 cost 값을 변환 전으로 되돌리기 => variance 필요
# 현재 mcmc 샘플은 precision 임 => variance로 바꾸기

## 방법 1 : forloop 사용 
g0_sigma11 <- c()
g0_sigma21 <- c()
g0_sigma12 <- c()
g0_sigma22 <- c()
for (i in 1:nrow(sample)) {
  a<- sample$g0_sig11[i]
  b<- sample$g0_sig21[i]
  c<- sample$g0_sig12[i]
  d<- sample$g0_sig22[i]
  
  g0_sigma11[i] <- d/(a*d-b*c)
  g0_sigma21[i] <- -c/(a*d-b*c)
  g0_sigma12[i] <- -b/(a*d-b*c)
  g0_sigma22[i] <- a/(a*d-b*c)
}
Inv_var_g0 <- data.frame(g0_sigma11, g0_sigma21, g0_sigma12, g0_sigma22)

# 방법 2 : 벡터를 통째로연산 
Inverse <- function(a,b,c,d) {
  sigma11 <- d/(a*d-b*c)
  sigma21 <- -c/(a*d-b*c)
  sigma12 <- -b/(a*d-b*c)
  sigma22 <- a/(a*d-b*c)
  df <- data.frame(sigma11, sigma21, sigma12, sigma22)
  return(df)
}

Inv_var_g1 <- Inverse(sample$g1_sig11, sample$g1_sig21, 
                      sample$g1_sig12, sample$g1_sig22)
colnames(Inv_var_g1) <- c('g1_sigma11', 'g1_sigma21', 'g1_sigma12',
                          'g1_sigma22') 

# 기존 sample에 variance 합치기
sample_new <- cbind(sample, Inv_var_g0, Inv_var_g1)

# log 변환된 Cost를 로그 변환 전으로 다시 되돌리기
lognormal_mean <- function(mu, sigma) {
  new_mu <- exp(mu + sigma/2)
  return(new_mu)
}
sample_new$g0_mean_cost <- lognormal_mean(sample_new$g0_mean_logc, sample_new$g0_sigma22)
sample_new$g1_mean_cost <- lognormal_mean(sample_new$g1_mean_logc, sample_new$g1_sigma22)

head(sample_new)

# 새로운 dataset 저장하기
write.csv(sample_new, "C:/Users/soyou/Dropbox/대체보고서/MCMC/MCMC_samples_0913_2.csv", row.names = F)
colnames(sample_new)

# Willingness to Pay에 따른 P(INNB > 0 | WTP, data) 확률 구하기

new_df <- sample_new[,c('g0_mean_e', 'g0_mean_cost', 'g1_mean_e', 'g1_mean_cost')]

k_list <- seq(1000, 7000, 10)

prob <- c()
for (k in 1:length(k_list)) {
  lambda_v <- c(-k_list[k], 1, k_list[k], -1)
  INB <- c()
  p <- c()
  for (i in 1:nrow(new_df)) {
    mean_vector <- c()
    for (j in 1:4) {
      mean_vector[j] <- new_df[[i, j]]
    }
    INB[i] <- crossprod(lambda_v, mean_vector)
    if (INB[i] > 0) {
      p[i] <- 1
    }
    else {
      p[i] <- 0
    }
  }
  prob[k] <- sum(p) / length(p)
}
round(prob,2)
plot <- data.frame(k_list, prob)
plot %>% filter(prob >=0.5 & prob < 0.6)

# Cost-effectiveness Acceptability Curve
plot(x = 3420, y = 0.5, xlab = "Willingness to Pay", ylab = "Probability"
     , xlim = c(1000,7000), ylim=c(0,1), pch = 16, col = 'red',
     main = "Cost-Effectiveness Acceptability Curve")
text(x = 4000,y= 0.43, label = "(3420,0.5)", col = 'red')
lines(k_list, prob)
abline(h = 0.5,col = 'red', lty = 2)
abline(v = 3420, col ='red', lty = 2)

# 베이지안으로 추정한 ICER
inc_eff <- mean(new_df$g1_mean_e - new_df$g0_mean_e)
inc_cost <- mean(new_df$g1_mean_cost - new_df$g0_mean_cost)

icer <- inc_cost / inc_eff


######## C/E Plane ##########
sample_new <- read.csv("C:/Users/Soyoung Han/Dropbox/대체보고서/MCMC/MCMC_samples_0913_2.csv")

head(sample_new)

sample_new$diff_effect <- sample_new$g1_mean_e - sample_new$g0_mean_e
sample_new$diff_cost <- sample_new$g1_mean_cost - sample_new$g0_mean_cost

cost_diff_list <- sample_new$diff_cost
eff_diff_list <- sample_new$diff_effect
df_plot <- data.frame(ie = eff_diff_list, ic = cost_diff_list)

# plane 그리기
ylim <- max(cost_diff_list) * 1.1
xlim <- ceiling(max(eff_diff_list) * 1.1)
x_range <- seq(-70, 70, 0.01)
shaded_region_data <- data.frame(x = x_range, y = 3420*x_range)
#shaded_region_data2 <- data.frame(x = seq(ylim/3420, 70, 0.01))
ggplot() + 
  geom_jitter(data = df_plot, aes(x = ie, y = ic), size = .5)  + 
  geom_line(data = shaded_region_data, aes(x =x, y= y), color = 'blue') +
  geom_ribbon(data = shaded_region_data,aes(x=x, ymin=-ylim, ymax=y), fill="blue", alpha=0.1) +
  #geom_ribbon(data = shaded_region_data2,aes(x=x, ymin=-Inf, ymax=Inf), fill="blue", alpha=0.1) +
  #geom_text(x=40, y=ylim, label="*ICER = 3,297.106", col = 'red') +
  #geom_text(x=45, y=50000, label=paste("WTP =",wtp), col = 'blue') +
  xlab("Incremental score") + 
  ylab("Incremental cost") +
  scale_y_continuous(limits = c(-ylim, ylim),expand = c(0,0)) +
  scale_x_continuous(limits = c(-xlim, xlim), breaks = seq(-100, 100, 20),
                     expand = c(0,0)) +
  theme(legend.position = "bottom") + 
  scale_colour_discrete(name = "Strategy") +
  geom_hline(yintercept = 0) + 
  geom_vline(xintercept = 0) +
  labs(title = "Cost-Effectiveness Plane", subtitle = "WTP = 3,420")