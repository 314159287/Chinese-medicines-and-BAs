library(readxl)
library(ggplot2)
library(tidyr)

df <- read_excel("C:/Users/pc/Desktop/admet汇总.xlsx")

# 移除SMILES列和坐标列
df <- df[, !names(df) %in% c("smiles", "molstr", "Alarm_NMR", "BMS", "Chelating", 
                             "PAINS", "NonBiodegradable", "NonGenotoxic_Carcinogenicity", 
                             "SureChEMBL", "LD50_oral", "Skin_Sensitization", 
                             "Acute_Aquatic_Toxicity", "FAF-Drugs4 Rule",
                             "Genotoxic_Carcinogenicity_Mutagenicity")]

# 数据转换
df[] <- lapply(df, function(x) as.numeric(as.character(x)))

# 列名
column_names <- names(df)

for (col in column_names) {
  # 直方图
  p <- ggplot(df, aes_string(x = paste0("`", col, "`"))) +  
    geom_histogram(bins = 30, fill = "red", color = "black") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 90, hjust = 1),
          plot.background = element_rect(fill = "white")) +
    labs(title = paste("visualisation of", col),
         x = col,
         y = "frequency")
  
  print(p)
  
  # 保存
  ggsave(filename = file.path("C:/Users/pc/Desktop/ADMET可视化", paste(col, ".png", sep = "")), 
         plot = p, 
         width = 10, 
         height = 5)
}

