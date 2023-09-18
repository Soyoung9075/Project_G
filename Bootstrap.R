################## ICER 계산 #########################


# 강남3구+성북구와 그외 지역을 구분하기 (컬럼 추가, 강남4구 = 1, 그외 = 0)
df_total2 <- df_total %>% mutate(region = case_when(구 %in% c('강남구', '서초구', '송파구', '강동구') ~ 1,
                                                    TRUE ~ 0))
df_total2 %>% select(region) %>% group_by(region) %>% summarise(n = n())
write.csv(df_total2, 'seoul_score_cost_0913.csv', row.names = F) # 여기까지 저장

# ICER값 계산하기
mean_eff_A <- mean(df_total2[df_total2$region == 1,]$q_score)
mean_eff_B <- mean(df_total2[df_total2$region == 0,]$q_score)

mean_cost_A <- mean(df_total2[df_total2$region == 1,]$total_cost)
mean_cost_B <- mean(df_total2[df_total2$region == 0,]$total_cost)

icer<-(mean_cost_A - mean_cost_B) / (mean_eff_A - mean_eff_B)


################### Bootstrap ###################

# 데이터 프레임 나누기
df_group1 <- df_total2 %>% filter(region == 1)
df_group2 <- df_total2 %>% filter(region == 0)

#  부트스트랩 알고리즘 짜기
B = 1000
ratio_list <- c()
cost_diff_list <- c()
eff_diff_list <- c()
set.seed(0)

for (n in 1:B) {
  which_1 <- sample(1:nrow(df_group1), 5, replace = TRUE)
  which_2 <- sample(1:nrow(df_group2), 10, replace = TRUE)
  
  sample1_cost <- df_group1[which_1,]$total_cost
  sample2_cost <- df_group2[which_2,]$total_cost
  sample1_eff <- df_group1[which_1,]$q_score
  sample2_eff <- df_group2[which_2,]$q_score
  
  sample1_mean_cost <- mean(sample1_cost)
  sample2_mean_cost <- mean(sample2_cost)
  sample1_mean_eff <- mean(sample1_eff)
  sample2_mean_eff <- mean(sample2_eff)
  
  corrected_sample1_cost <- c()
  corrected_sample2_cost <- c()
  corrected_sample1_eff <- c()
  corrected_sample2_eff <- c()
  
  correction <- function(sample, N, mean) {
    sample*sqrt(N / (N-1)) + mean*(1-sqrt(N / (N-1)))
  }
  
  for (i in 1:length(which_1)) {
    corrected_sample1_cost[i] <- correction(sample1_cost[i], length(sample1_cost), sample1_mean_cost)
    corrected_sample1_eff[i] <- correction(sample1_eff[i], length(sample1_eff), sample1_mean_eff)
  }
  
  for (i in 1:length(which_2)) {
    corrected_sample2_cost[i] <- correction(sample2_cost[i], length(sample2_cost), sample2_mean_cost)
    corrected_sample2_eff[i] <- correction(sample2_eff[i], length(sample2_eff), sample2_mean_eff)
  }
  
  cost_diff <- mean(corrected_sample1_cost) - mean(corrected_sample2_cost)
  eff_diff <- mean(corrected_sample1_eff) - mean(corrected_sample2_eff)
  ratio <- cost_diff / eff_diff
  
  ratio_list[n] <- ratio
  cost_diff_list[n] <- cost_diff
  eff_diff_list[n] <- eff_diff
}
min(ratio_list) # 221.087
max(ratio_list) # 2592.344
ceiling()
df_plot <- data.frame(ie = eff_diff_list, ic = cost_diff_list)

# bootstrap 결과 저장
write.csv(df_plot, 'C:\\Users\\soyou\\Dropbox\\대체보고서\\분양 데이터\\merge\\bootstrap_0913.csv', row.names = F)

# Cost-Effectiveness plane 그리기
ylim <- max(cost_diff_list) * 1.1
xlim <- ceiling(max(eff_diff_list) * 1.1)
ggplot(data = df_plot, aes(x = ie, y = ic)) + 
  geom_jitter(size = .5)  + 
  xlab("Incremental score") + 
  ylab("Incremental cost") +
  scale_y_continuous(limits = c(-ylim, ylim)) +
  scale_x_continuous(limits = c(-xlim, xlim), breaks = seq(-100, 100, 20)) +
  theme(legend.position = "bottom") + 
  scale_colour_discrete(name = "Strategy") +
  geom_abline(slope = 1000, linetype = "dashed") +
  geom_hline(yintercept = 0) + 
  geom_vline(xintercept = 0)

# 점추정한 ICER 표시
df_icer <- data.frame(ie = 20.33, ic = 63245.25)
wtp <- 4000
ggplot(data = df_icer, aes(x = ie, y = ic)) + 
  geom_point(size = 2, color = "red")  + 
  xlab("Incremental score") + 
  ylab("Incremental cost") +
  scale_y_continuous(limits = c(-ylim, ylim)) +
  scale_x_continuous(limits = c(-xlim, xlim), breaks = seq(-100, 100, 20)) +
  theme(legend.position = "bottom") + 
  scale_colour_discrete(name = "Strategy") +
  geom_abline(slope = wtp,col = "blue") +
  geom_hline(yintercept = 0) + 
  geom_vline(xintercept = 0) +
  geom_text(x=38, y=60000, label="*ICER = 3,111.001", col = 'red') +
  geom_text(x=50, y=150000, label=paste("WTP =",wtp), col = 'blue') +
  labs(title = "Cost-Effectiveness Plane") +
  theme(plot.title=element_text(hjust=0.5))

# bootstrap + 점추정
df_plot <- data.frame(ie = eff_diff_list, ic = cost_diff_list)
# plane 그리기
ylim <- max(cost_diff_list) * 1.1
xlim <- ceiling(max(eff_diff_list) * 1.1)
x_range <- seq(-70, 70, 0.01)
shaded_region_data <- data.frame(x = x_range, y = 4000*x_range)
shaded_region_data2 <- data.frame(x = seq(ylim/4000, 70, 0.01))
ggplot() + 
  geom_jitter(data = df_plot, aes(x = ie, y = ic), size = .5)  + 
  geom_point(data = df_icer, aes(x = ie, y = ic), size = 2, color = "red") +
  geom_line(data = shaded_region_data, aes(x =x, y= y), color = 'blue') +
  geom_ribbon(data = shaded_region_data,aes(x=x, ymin=-ylim, ymax=y), fill="blue", alpha=0.1) +
  geom_ribbon(data = shaded_region_data2,aes(x=x, ymin=-Inf, ymax=Inf), fill="blue", alpha=0.1) +
  geom_text(x=40, y=ylim, label="*ICER = 3,297.106", col = 'red') +
  geom_text(x=45, y=50000, label=paste("WTP =",wtp), col = 'blue') +
  xlab("Incremental score") + 
  ylab("Incremental cost") +
  scale_y_continuous(limits = c(-ylim, ylim),expand = c(0,0)) +
  scale_x_continuous(limits = c(-xlim, xlim), breaks = seq(-100, 100, 20),
                     expand = c(0,0)) +
  theme(legend.position = "bottom") + 
  scale_colour_discrete(name = "Strategy") +
  geom_hline(yintercept = 0) + 
  geom_vline(xintercept = 0) +
  labs(title = "Cost-Effectiveness Plane", subtitle = "WTP = 4,000")

# 부트스트랩 icer 계산 한후 오름차순 정리
df2 <- df %>% mutate(icer = ic/ie) %>% arrange(icer)

# 부트스트랩 신뢰구간 구하기 
quantile(df2$icer, probs = c(0.05, 0.95))
icer_list <- df2$icer
icer_list[26]
icer_list[975]

# 부트스트랩 Cost-Effectiveness Acceptability Curve 그리기 

wtp <- seq(1000,7000,1)
prob <- c()

for (i in 1:length(wtp)) {
  Temp <- df2 %>% mutate(innb = ie*wtp[i] - ic) %>% mutate(result = case_when(
    innb > 0 ~ 1,
    TRUE ~ 0
  ))
  prob[i] <- sum(Temp$result) / length(Temp$result)
}

plot(x = 3158, y = 0.5, xlab = "Willingness to Pay", ylab = "Proportion"
     , xlim = c(1000,7000), ylim=c(0,0.9), pch = 16, col = 'red',
     main = "Cost-Effectiveness Acceptability Curve")
text(x = 3800,y= 0.43, label = "(3158,0.5)", col = 'red')
lines(wtp, prob)
abline(h = 0.5,col = 'red', lty = 2)
abline(v = 3158, col ='red', lty = 2)

# 확률이 0.5인 wtp 값 확인
dt <- data.frame(wtp, prob)
dt %>% filter(prob>=0.5)