################## Effect score modellig ######################

library(tidyverse)

df <- read.csv('C:\\Users\\soyou\\Dropbox\\대체보고서\\분양 데이터\\merge\\seoul_merge_forR.csv')
colnames(df)

colnames(df) <- c('아파트명','전용면적_분류','구','호선','브랜드여부','세대수','소형평수비중','중형평수비중',
                  '대형평수비중','인근_지하철_호선수','지하철도보_분','을지로','강남','초등학교도보_분','공급면적','전세가율_평균','승하차총객수_노선기준',
                  '승하차총객수_역기준','학업성취도평균','특목고_진학률','상위','순위','공급금액','매매평균가','매매_분양가gap',
                  '취득세', '농어촌특별세', '지방교육세', '비투기과열지구', '투기과열지구',
                  '투기과열_prob', 'weighted_cost', 'tax', 'total_cost')

# 모델링용 데이터셋 만들기 
df_gap <- df %>% select(-c('아파트명', '전용면적_분류', '공급금액', '매매평균가',
                           '취득세', '농어촌특별세', '지방교육세', '비투기과열지구', '투기과열지구',
                           '투기과열_prob', 'weighted_cost', 'tax', 'total_cost')) %>%
  subset(!is.na(df[['매매_분양가gap']]))

# 삭제된 행수
nrow(df) - nrow(df_gap) 

# categorical variable factor로 만들기
df_gap$구 <- as.factor(df_gap$구)
df_gap$호선 <- as.factor(df_gap$호선)
df_gap$브랜드여부 <- as.factor(df_gap$브랜드여부)

# 매매평균가를 0-1로 scaling
min_max <- function(x) {
  return((x-min(x))/(max(x)-min(x)))
}

# predictors 표준화 standardization
conti_feature = feature_list[-c(1, 2, 3)]  # continous value만 선택
df_gap_2 <- df_gap %>% mutate_at(conti_feature, ~min_max(.) %>% as.vector) %>% 
  mutate_at(c('매매_분양가gap'), ~min_max(.) %>% as.vector)

# linear regression 식 만들기
column_list <- colnames(df_gap)
feature_list <- column_list[column_list != '매매_분양가gap']
labels = paste(feature_list, collapse = "+")
formula = as.formula(paste0("매매_분양가gap~", labels))
formula

# Backward 방식으로 Feature selection
step(lm(매매_분양가gap ~ 브랜드여부 + 세대수 + 
          소형평수비중 + 중형평수비중 + 대형평수비중 + 지하철도보_분 + 을지로 + 
          강남 + 초등학교도보_분 + 공급면적 + 승하차총객수_노선기준 + 승하차총객수_역기준 +
          학업성취도평균 + 특목고_진학률 + 상위, df_gap_2), direction = "backward")


# 최종 Modeling
model_1 <- lm(매매_분양가gap ~ 브랜드여부 +  
                소형평수비중 + 중형평수비중 + 강남 + 공급면적 + 승하차총객수_역기준 
              + 특목고_진학률 + 상위, df_gap_2)
summary(model_1)

# coefficients 만 뽑아내기 

row_name = rownames(summary(model_1)$coefficients)[-(1)]
coef_list = c()
for (i in 1:length(row_name)) {
  coef_list[i] <- summary(model_1)$coefficients[row_name[i], "Estimate"]
}

# 점수화
score_list = (coef_list / abs(sum(coef_list))) * 100

# score_card 만들기
score_card = data.frame(attribute = row_name, score = score_list)


# score 계산을 위한 data set 만들기
df_gap_2 <- df_gap_2 %>% mutate(브랜드여부Y = recode(브랜드여부, "Y" = 1, "N" = 0))
temp <- df_gap_2 %>% select(브랜드여부Y, 소형평수비중, 중형평수비중, 강남, 공급면적, 승하차총객수_역기준, 특목고_진학률, 상위)
head(temp)
rownames(temp) <- NULL # index reset

# 총점 계산하기
empty_df <- data.frame()
for (i in 1:nrow(temp)) {
  row_df <- temp[i,] * score_card[,'score']
  empty_df <- bind_rows(empty_df, row_df)
}

empty_df$총점 <- rowSums(empty_df)
new_score <- empty_df$총점 + 100

# 분포 확인하기 : histogram
hist(new_score, breaks = 30, prob = TRUE)
lines(density(new_score), col = "red")

# 기존 전체 데이터셋에 총점 붙이기
df_total = subset(df, !is.na(df[['매매_분양가gap']]))
rownames(df_total) <- NULL
df_total$score <- new_score

# 분위수로 변환하기
df_total <- df_total %>% arrange(score)
sorted_score <-df_total$score
quantile_value <- c()
for (i in 1:length(sorted_score)) {
  quantile_value[i] <- quantile(sorted_score, probs = i / max(sorted_score))
}
df_total$q_score <- quantile_value

# 매매-분양가gap과 score 사이의 correlation 확인
cor <- cor(df_total$매매_분양가gap, df_total$q_score)
plot(df_total$매매_분양가gap, df_total$q_score, xlab = "매매-분양가 GAP", ylab = "투자매력도점수",
     main = paste("correlation :", round(cor,2)))
abline(lm(df_total$q_score ~ df_total$매매_분양가gap), col = "red")

# 저장하기
setwd('C:\\Users\\soyou\\Dropbox\\대체보고서\\분양 데이터\\merge')
write.csv(df_total, 'seoul_score_cost_0913.csv', row.names = F)