from pyspark.sql.window import Window
from pyspark.sql import functions as F

# spark 기본 문법 (polars와 매우 비슷)
df.filter()
df.withColumn()
df.select()
df.collect()
df.groupBy()

F.col(col_name)
df.groupBy(col_name).agg(F.avg('age'), F.count('*')).show()
df.orderBy()
F.count()
F.countDistinct()
F.avg()
F.mean()
F.sum()
F.min()
F.max()

df.na.drop()
df.na.fill({col_name: fill_value})
df.isNull()
df1.join(
			df2,
			on = col_name,
			how = 'inner'
	)



# window 함수
window_spec = Window.partitionBy("user_id").orderBy("date")

df.withColumn("row_num", F.row_number().over(window_spec))

"변화량 계산"
window_spec = Window.partitionBy("user_id").orderBy("date")

df_with_diff = df.withColumn("prev_amount", F.lag("amount", 1).over(window_sepc))\
				.withColumn("diff", F.col("amount") - F.col("prev_amount"))


"누적 비율 계산"
window_spec = Window.partitionBy("user_id").orderBy("date")\
				.rowsBetween(Window.unboundedPreceding, Window.currentRow)

"누적합 먼저 계산"
df = df.withColumn("cumsum", F.sum("amount").over(window_spec))

"전체 합 계산"
total_sum = df.groupBy("user_id").agg(F.sum("amount").alias("total_amount"))

"누적 비율 계산"
df = df.join(total_sum, on = "user_id", how = "left")
df = df.withColumn("cumulative_ratio", F.col("cumsum") / F.col("total_amount"))


"Top-N 추출"
window_spec = Window.partitionBy("user_id").orderBy(F.desc("date"))

df_ranked = df.withColumn("rank", F.row_number().over(window_spec))
top3 = df_ranked.filter(F.col("rank") <= 3)


"최초값/최대값 계산"
window_spec = Window.partitionBy("user_id")

df = df.withColumn("first_amount", F.first("amount").over(window_spec))\
		.withColumn("max_amount", F.max("amount").over(window_spec))