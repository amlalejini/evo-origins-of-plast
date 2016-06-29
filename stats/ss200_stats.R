
df <- read.table("../visualization/data/ss200_final_dominant_overview.csv", header=TRUE, row.name=1, sep=",")

# Create contingency table
treatments <- c("baseline", "low-mut", "high-mut", "cycle-50", "cycle-200")
baseConditions <- c("unrestricted")
compConditions <- c("uncon-restricted", "subopt-restricted", "full-restricted")

for (treatment in treatments) {
  for (baseCondition in baseConditions) {
    for (compCondition in compConditions) {
      #cat(treatment, ": ", baseCondition, " vs. ", compCondition, "\n")
      # Build my contingency table
      print("========================================================")
      cat(paste(treatment, baseCondition, sep = "-"), " vs. ", paste(treatment, compCondition, sep = "-"), "\n" )
      
      baseIsPlastic <- df[paste(treatment, baseCondition, sep = "-"), "total_plastic"]
      compIsPlastic <- df[paste(treatment, compCondition, sep = "-"), "total_plastic"]
      baseTotal <- df[paste(treatment, baseCondition, sep = "-"), "total"]
      compTotal <- df[paste(treatment, compCondition, sep = "-"), "total"]
      v <- c(baseIsPlastic, baseTotal - baseIsPlastic, compIsPlastic, compTotal - compIsPlastic)
      colNames = c(paste(treatment, baseCondition, sep = "-"), paste(treatment, compCondition, sep = "-"))
      rowNames = c("plastic", "not_plastic")
      m <- matrix(v, nrow = 2, ncol = 2, dimnames = list(rowNames, colNames))
      print("Contingency Table: " )
      print (m)
      print(fisher.test(m, alternative = "two.sided"))
    }
  }
}

