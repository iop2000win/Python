'''
Polars 라이브러리 활용에 대한 내용 정리

- 개요
Rust로 개발

멀티스레딩과 병렬 처리를 지원
단일 머신의 자원을 최대한 활용할 수 있도록 병렬 처리와 벡터화 연산을 통해 컬럼 기반 처리를 최적화


polars.DataFrame

- polars.LazyFrame
즉각적으로 연산을 하는 것이 아니라 쿼리 플랜만 담아두고 있다가 값이 필요할 때,
즉 구체화할 때 collect() 함수를 호출하여 연산하는 방식
'''

# Eager API - 즉각 연산
df = pl.read_parquet("predicted_data-1.parquet")
result = (
			df
				.filter(
						pl.col("distance") >= 2
						& pl.col("created_hour").is_in([11, 12, 13, 18, 19, 20])
						)
				.group_by("pickup_zone_id")
				.agg(
	    				pl.mean("delivery_time").alias("avg_delivery_time")
					)
		)

# Lazy API (scan_parquet 함수 사용과 마지막 collect 함수 호출이 유일한 차이) - Lazy 연산
df = pl.scan_parquet("predicted_data-1.parquet")
result = (
			df
				.filter(
						pl.col("distance") >= 2
						& pl.col("created_hour").is_in([11, 12, 13, 18, 19, 20])
						)
				.group_by("pickup_zone_id")
				.agg(
    					pl.mean("delivery_time").alias("avg_delivery_time")
					)
		).collect(streaming = False) # True로 할 경우, Out of Core 기능 사용

'''
어떤 최적화가 이루어지기 이렇게 큰 속도 차이가 날까?

간단하게 설명하자면,
즉각 연산의 경우, parquet 파일 전체를 읽어온 뒤에 필터 및 집계 연산을 진행한다.
반면에 Lazy 연산의 경우, parquet파일을 스캔만 한 상태에서 필터 및 집계 연산을 통해
추출해야할 데이터를 연산한 후에 필요한 데이터만 추출하는 방식이다.
'''


'''
streaming 기능
Out of Core(External memory 알고리즘)
머신의 메모리 용량을 초과하는 매우 큰 데이터셋을 처리하게 해주는 기능
데이터를 작은 청크 단위 또는 연산 단위로 쪼개어 점진적으로 처리하는 방식으로
전체 데이터를 메모리에 한 번에 로드하지 않기 때문에 메모리 부분에서 강점이 있다.
'''



'''
Polars 문법
'''
import polars as pl
import pandas as pd
# ------------------------------------------------------------
# make and read data
#
# pl.DataFrame([value_list1, value_list2, ..., value_listN], schema = , orient = (default = None(col based)))
# pl.DataFrame({col_name: value_list, col_name: value_list, ...}, schema = )
# pl.read_csv()
# pl.read_excel()
# pl.read_parquet()
# pl.read_database(query = , connection = )
# ------------------------------------------------------------
'''

기본적으로 데이터의 값을 배열로 전달한다.
딕셔너리 형태로 테이블을 만들 때는 {key:value} = {컬럼명:컬럼값} 형태로 전달하면 된다.
각 컬럼에 대해서 데이터 타입을 지정하고 싶을 경우 schema 변수를 이용하면 된다.
값들만 배열로 전달할 경우에는 schema 변수를 통해 컬럼명 및 데이터 타입을 지정해줄 수 있다.
+) 배열만 전달할 경우 orient 변수를 통해 배열의 열기준/행기준을 정할수 있다.
   기본적으로는 열기준으로 처리된다.
'''
vendor_id = ['A', 'A', 'B', 'B', 'B']
passenger_count = [1, 1, 2, 2, 1]
trip_distance = [0.95, 1.2, 2.51, 2.9, 1.53]
payment_type = ['card', 'card', 'cash', 'cash', 'card']
total_amount = [14.3, 16.9, 34.6, 27.8, 15.2]

pl_df = pl.DataFrame([vendor_id, passenger_count, trip_distance, payment_type, total_amount]) # orient = 'col' 결과와 동일
pl_df_row = pl.DataFrame([vendor_id, passenger_count, trip_distance, payment_type, total_amount], orient = 'row')
print(pl_df)
print(pl_df_row)
'''
shape: (5, 5)
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ column_0 ┆ column_1 ┆ column_2 ┆ column_3 ┆ column_4 │
│ ---      ┆ ---      ┆ ---      ┆ ---      ┆ ---      │
│ str      ┆ i64      ┆ f64      ┆ str      ┆ f64      │
╞══════════╪══════════╪══════════╪══════════╪══════════╡
│ A        ┆ 1        ┆ 0.95     ┆ card     ┆ 14.3     │
│ A        ┆ 1        ┆ 1.2      ┆ card     ┆ 16.9     │
│ B        ┆ 2        ┆ 2.51     ┆ cash     ┆ 34.6     │
│ B        ┆ 2        ┆ 2.9      ┆ cash     ┆ 27.8     │
│ B        ┆ 1        ┆ 1.53     ┆ card     ┆ 15.2     │
└──────────┴──────────┴──────────┴──────────┴──────────┘
컬럼명이 없다.

+) 행기준으로 데이터 프레임을 만들 경우,
shape: (5, 5)
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ column_0 ┆ column_1 ┆ column_2 ┆ column_3 ┆ column_4 │
│ ---      ┆ ---      ┆ ---      ┆ ---      ┆ ---      │
│ str      ┆ str      ┆ str      ┆ str      ┆ str      │
╞══════════╪══════════╪══════════╪══════════╪══════════╡
│ A        ┆ A        ┆ B        ┆ B        ┆ B        │
│ 1        ┆ 1        ┆ 2        ┆ 2        ┆ 1        │
│ 0.95     ┆ 1.2      ┆ 2.51     ┆ 2.9      ┆ 1.53     │
│ card     ┆ card     ┆ cash     ┆ cash     ┆ card     │
│ 14.3     ┆ 16.9     ┆ 34.6     ┆ 27.8     ┆ 15.2     │
└──────────┴──────────┴──────────┴──────────┴──────────┘
'''

pl_df = pl.DataFrame(
						[vendor_id, passenger_count, trip_distance, payment_type, total_amount],
						schema = ['vendor_id', 'passenger_count', 'trip_distance', 'payment_type', 'total_amount']
					)
'''
shape: (5, 5)
┌───────────┬─────────────────┬───────────────┬──────────────┬──────────────┐
│ vendor_id ┆ passenger_count ┆ trip_distance ┆ payment_type ┆ total_amount │
│ ---       ┆ ---             ┆ ---           ┆ ---          ┆ ---          │
│ str       ┆ i64             ┆ f64           ┆ str          ┆ f64          │
╞═══════════╪═════════════════╪═══════════════╪══════════════╪══════════════╡
│ A         ┆ 1               ┆ 0.95          ┆ card         ┆ 14.3         │
│ A         ┆ 1               ┆ 1.2           ┆ card         ┆ 16.9         │
│ B         ┆ 2               ┆ 2.51          ┆ cash         ┆ 34.6         │
│ B         ┆ 2               ┆ 2.9           ┆ cash         ┆ 27.8         │
│ B         ┆ 1               ┆ 1.53          ┆ card         ┆ 15.2         │
└───────────┴─────────────────┴───────────────┴──────────────┴──────────────┘
'''

pl_df = pl.DataFrame(
						{
							'vendor_id': vendor_id,
							'passenger_count': passenger_count,
							'trip_distance': trip_distance,
							'payment_type': payment_type,
							'total_amount': total_amount
						},
						# schema = {
						# 			'vendor_id': str,
						# 			'passenger_count': int,
						# 			'trip_distance': float,
						# 			'payment_type': str,
						# 			'total_amount': float
						# }
				)
'''
해당 방법이 가장 활용도가 높을 것으로 보인다.

shape: (5, 5)
┌───────────┬─────────────────┬───────────────┬──────────────┬──────────────┐
│ vendor_id ┆ passenger_count ┆ trip_distance ┆ payment_type ┆ total_amount │
│ ---       ┆ ---             ┆ ---           ┆ ---          ┆ ---          │
│ str       ┆ i64             ┆ f64           ┆ str          ┆ f64          │
╞═══════════╪═════════════════╪═══════════════╪══════════════╪══════════════╡
│ A         ┆ 1               ┆ 0.95          ┆ card         ┆ 14.3         │
│ A         ┆ 1               ┆ 1.2           ┆ card         ┆ 16.9         │
│ B         ┆ 2               ┆ 2.51          ┆ cash         ┆ 34.6         │
│ B         ┆ 2               ┆ 2.9           ┆ cash         ┆ 27.8         │
│ B         ┆ 1               ┆ 1.53          ┆ card         ┆ 15.2         │
└───────────┴─────────────────┴───────────────┴──────────────┴──────────────┘
'''

pl_taxi_df = pl.read_parquet('file_path')
'''
shape: (5, 19)
┌──────────┬──────────────┬──────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬─────────────┐
│ VendorID ┆ tpep_pickup_ ┆ tpep_dropoff ┆ passenger_co ┆ … ┆ improvement_ ┆ total_amount ┆ congestion_s ┆ Airport_fee │
│ ---      ┆ datetime     ┆ _datetime    ┆ unt          ┆   ┆ surcharge    ┆ ---          ┆ urcharge     ┆ ---         │
│ i32      ┆ ---          ┆ ---          ┆ ---          ┆   ┆ ---          ┆ f64          ┆ ---          ┆ f64         │
│          ┆ datetime[μs] ┆ datetime[μs] ┆ i64          ┆   ┆ f64          ┆              ┆ f64          ┆             │
╞══════════╪══════════════╪══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪═════════════╡
│ 2        ┆ 2024-12-01   ┆ 2024-12-01   ┆ 1            ┆ … ┆ 1.0          ┆ 51.97        ┆ 0.0          ┆ 1.75        │
│          ┆ 00:12:27     ┆ 00:31:12     ┆              ┆   ┆              ┆              ┆              ┆             │
│ 2        ┆ 2024-11-30   ┆ 2024-12-01   ┆ 1            ┆ … ┆ 1.0          ┆ 50.76        ┆ 2.5          ┆ 0.0         │
│          ┆ 23:56:04     ┆ 00:28:15     ┆              ┆   ┆              ┆              ┆              ┆             │
│ 2        ┆ 2024-12-01   ┆ 2024-12-01   ┆ 4            ┆ … ┆ 1.0          ┆ 82.69        ┆ 2.5          ┆ 1.75        │
│          ┆ 00:50:35     ┆ 01:24:46     ┆              ┆   ┆              ┆              ┆              ┆             │
│ 2        ┆ 2024-12-01   ┆ 2024-12-01   ┆ 3            ┆ … ┆ 1.0          ┆ 24.72        ┆ 2.5          ┆ 0.0         │
│          ┆ 00:18:16     ┆ 00:33:16     ┆              ┆   ┆              ┆              ┆              ┆             │
│ 2        ┆ 2024-12-01   ┆ 2024-12-01   ┆ 1            ┆ … ┆ 1.0          ┆ 36.8         ┆ 2.5          ┆ 0.0         │
│          ┆ 00:56:13     ┆ 01:18:25     ┆              ┆   ┆              ┆              ┆              ┆             │
└──────────┴──────────────┴──────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴─────────────┘
'''

# ------------------------------------------------------------
# 컬럼 선택
# df.select()
# pl.col()
# pl.col().exclude()
# df.drop()
# polars.selectors
# ------------------------------------------------------------
'''
컬럼을 선택하는 방법은 매우 다양하다.
pandas와 동일하게 대괄호를 통해 선택하는 것이 가능하다.
다만, polars는 체인 연산 및 선택과 연산을 한 번에 처리하는 것이 매우 편한데
대괄호 방식을 활용하면 이를 활용하는 것이 어렵다.
그러므로 단순히 원하는 컬럼만 선택해서 보고 싶을 경우에는 대괄호를 통한 선택이 간편하지만,
.select(pl.col()) 메서드를 활용하는 방법에 익숙해지는 것이 좋다.

pl.col()은 polars에서 컬럼을 나타내는 표현식인데 이를 활용해 단순한 선택과 기본 연산 뿐 아니라,
다양한 체인 연산과 함수 적용까지 가능하다.

select, drop 메서드는 새로운 데이터 프레임을 리턴하는 함수이다.
따라서 df 자체가 바뀌는 것이 아니므로 해당 결과로 데이터 프레임을 변경하고 싶을 경우,
변수에 해당 값을 다시 선언 해주어야 한다.
'''
print(pl_df[['vendor_id', 'passenger_count']])
print(pl_df.select(['vendor_id', 'passenger_count']))
print(pl_df.select(pl.col(['vendor_id', 'passenger_count'])))
print(pl_df.select(
					pl.col('vendor_id'),
					pl.col('passenger_count') # 각 컬럼에 대해서 메서드를 적용할 경우 컬럼을 이렇게 나열하면 유용하다.
				)
	)
# 모두 동일한 결과가 나온다.

# 한 개 컬럼만 추출할 경우 *시리즈와 데이터 프레임의 차이
print(pl_df.select(pl.col('vendor_id'))) # (n, 1) 형태의 데이터 프레임 반환
print(pl_df[['vendor_id']]) # (n, 1) 형태의 데이터 프레임 반환
print(pl_df['vendor_id']) # (1, ) 형태의 시리즈 반환
print(pl_df.select(pl.col('vendor_id')).to_series()) # to_series 메서드를 통해 시리즈 형태로 변환 가능


# 모든 컬럼 선택 및 특정 컬럼 제외
print(pl_df)
print(pl_df.select('*'))
print(pl_df.select(pl.col('*')))
print(pl_df.select(pl.all()))

print(pl_df.select(pl.col('*').exclude(['payment_type', 'total_amount'])))
print(pl_df.select(pl.all().exclude('payment_type', 'total_amount'))) # 리스트로 감싸서 입력해도 되고, 그냥 나열해도 된다.
print(pl_df.drop(['payment_type', 'total_amount']))


# selector 활용하기
import polars.selectors as cs
print(cs.integer())
print(cs.string())
print(cs.numeric())
print(cs.float())

print(pl_df.select(pl.col(pl.Float64, pl.String)))
print(pl_df.select(cs.float(), cs.string()))
# 해당 데이터 타입을 가진 컬럼들만 선택


# 정규표현식 사용 가능 - It should start with '^' and end with '$'
print(pl_df.select(pl.col('^.*(amount|count)$')))


# ------------------------------------------------------------
# value 선택
# 행이나 열 단위로 데이터를 처리하는 것이 아니라 특정 셀의 값을 추출하고 싶을 경우
# ------------------------------------------------------------
# vendor_id의 다섯 번째 값(index = 4)을 추출하고 싶은 경우라고 가정
# 시리즈의 경우 원하는 값의 인덱스를 입력하면 된다.
pl_seires = pl_df.select(pl.col('vendor_id')).to_series()
sample_val = pl_series[4] # 해당 값의 인덱스 입력

# 데이터 프레임의 경우 .item 메서드를 통해 원하는 좌표를 입력하면 된다.
sample_val = pl_df.item(4, 0) # vendor_id = 0번째 컬럼 (row, column), 컬럼의 경우 컬럼명을 전달해도 된다.
sample_val = pl_df.select(pl.col('vendor_id')).item(4, 0) # 이렇게 사용할 경우 컬럼의 경우 인덱스를 몰라도 된다.


# ------------------------------------------------------------
# null 값 처리
# ------------------------------------------------------------
'''
컬럼별로 결측치 수를 확인하고, 결측치를 어떻게 처리할 것인지 결정할 수 있다.
'''
pl_null_df = pl.DataFrame({
    "vendor_id": ["A", "A", "B", None, "B"],
    "passenger_count": [1, None, None, 2, 1],
    "trip_distance": [0.95, 1.2, None, 2.9, 1.53],
    "payment_type": ["card", "card", None, None, "card"],
    "total_amount": [14.3, 16.9, None, 27.8, 15.2]
})

print(pl_null_df.null_count())
print(pl_null_df.select(pl.col('*').is_null()).sum())
print(pl_null_df.select(pl.col('*').is_null()))
'''
shape: (1, 5)
┌───────────┬─────────────────┬───────────────┬──────────────┬──────────────┐
│ vendor_id ┆ passenger_count ┆ trip_distance ┆ payment_type ┆ total_amount │
│ ---       ┆ ---             ┆ ---           ┆ ---          ┆ ---          │
│ u32       ┆ u32             ┆ u32           ┆ u32          ┆ u32          │
╞═══════════╪═════════════════╪═══════════════╪══════════════╪══════════════╡
│ 1         ┆ 2               ┆ 1             ┆ 2            ┆ 1            │
└───────────┴─────────────────┴───────────────┴──────────────┴──────────────┘

shape: (5, 5)
┌───────────┬─────────────────┬───────────────┬──────────────┬──────────────┐
│ vendor_id ┆ passenger_count ┆ trip_distance ┆ payment_type ┆ total_amount │
│ ---       ┆ ---             ┆ ---           ┆ ---          ┆ ---          │
│ bool      ┆ bool            ┆ bool          ┆ bool         ┆ bool         │
╞═══════════╪═════════════════╪═══════════════╪══════════════╪══════════════╡
│ false     ┆ false           ┆ false         ┆ false        ┆ false        │
│ false     ┆ true            ┆ false         ┆ false        ┆ false        │
│ false     ┆ true            ┆ true          ┆ true         ┆ true         │
│ true      ┆ false           ┆ false         ┆ true         ┆ false        │
│ false     ┆ false           ┆ false         ┆ false        ┆ false        │
└───────────┴─────────────────┴───────────────┴──────────────┴──────────────┘
'''

pl_null_df.fill_null() # 특정 값으로 널 값을 채우는 메서드. 입력한 값의 데이터 타입에 대응하는 컬럼의 값만 채운다.
pl_null_df.fill_null(pl.lit()) # 각 컬럼에 맞는 데이터 타입으로 변형하여 널 값을 채운다.
pl_null_df.select(pl.col('*').fill_null()) # 컬럼을 지정하고 fill_null을 할 경우 pl.lit()메서드의 기능이 저절로 적용된다.
'''
shape: (5, 5)
┌───────────┬─────────────────┬───────────────┬──────────────┬──────────────┐
│ vendor_id ┆ passenger_count ┆ trip_distance ┆ payment_type ┆ total_amount │
│ ---       ┆ ---             ┆ ---           ┆ ---          ┆ ---          │
│ str       ┆ i64             ┆ f64           ┆ str          ┆ f64          │
╞═══════════╪═════════════════╪═══════════════╪══════════════╪══════════════╡
│ A         ┆ 1               ┆ 0.95          ┆ card         ┆ 14.3         │
│ A         ┆ 2               ┆ 1.2           ┆ card         ┆ 16.9         │
│ B         ┆ 2               ┆ 2.0           ┆ null         ┆ 2.0          │
│ null      ┆ 2               ┆ 2.9           ┆ null         ┆ 27.8         │
│ B         ┆ 1               ┆ 1.53          ┆ card         ┆ 15.2         │
└───────────┴─────────────────┴───────────────┴──────────────┴──────────────┘

shape: (5, 5)
┌───────────┬─────────────────┬───────────────┬──────────────┬──────────────┐
│ vendor_id ┆ passenger_count ┆ trip_distance ┆ payment_type ┆ total_amount │
│ ---       ┆ ---             ┆ ---           ┆ ---          ┆ ---          │
│ str       ┆ i64             ┆ f64           ┆ str          ┆ f64          │
╞═══════════╪═════════════════╪═══════════════╪══════════════╪══════════════╡
│ A         ┆ 1               ┆ 0.95          ┆ card         ┆ 14.3         │
│ A         ┆ 2               ┆ 1.2           ┆ card         ┆ 16.9         │
│ B         ┆ 2               ┆ 2.0           ┆ 2            ┆ 2.0          │
│ 2         ┆ 2               ┆ 2.9           ┆ 2            ┆ 27.8         │
│ B         ┆ 1               ┆ 1.53          ┆ card         ┆ 15.2         │
└───────────┴─────────────────┴───────────────┴──────────────┴──────────────┘
'''

# strategy = 'forward', 'backward', 'min', 'max', 'mean', 'zero', 'one'
# pl.median() - 중간 값으로 널 값을 채우는 방법
# interpolate() - 보간법을 통해 널 값을 채우는 방법
pl_null_df.fill_null(strategy = 'forward') # 앞의 값으로 채우기
pl_null_df.with_columns(pl.col('trip_distance').fill_null(pl.median('trip_distance'))) # 중간 값으로 채우기
pl_null_df.with_columns(pl.col(['trip_distance', 'total_amount']).fill_null(pl.median(['trip_distance', 'total_amount']))) # 한 번에 여러 컬럼에 대한 처리도 가능
pl_null_df.with_columns(pl.col(['trip_distance', 'total_amount']).interpolate()) # 해당 컬럼에 대해서 보간법으로 null 값을 채운다.


# ------------------------------------------------------------
# 기본 연산
# ------------------------------------------------------------
pl_df.select(
					(pl.col('passenger_count') +1).alias('with_driver'),
					(pl.col('trip_distance') -1).alias('trip_distance -1'),
					(pl.col('trip_distance') *1.60934).alias('trip_distance_km'),
					((pl.col('total_amount')/pl.col('trip_distance')).alias('total_amount / trip_distance'))
	)
'''
기본적인 연산은 pl.col()을 통해 계산 대상이 되는 컬럼을 지정한 후에 거기에 바로 연산을 진행하면 된다.
그렇게 할 경우 해당 컬럼의 모든 값들에 대해서 차원 형태의 계산이 진행된다.
컬럼과 컬럼 간의 연산도 동일하게 진행하면 된다.
다만 유의해야 할 점은 컬럼 연산을 진행하게 되면 기본적으로는 먼저 선언한 컬럼의 값이 연산 결과로 바뀌게 된다.
예를 들어 total_amount와 trip_distance 값을 더한다고 했을 때,
pl.col('total_amount') + pl.col('trip_distance') 라고 코드를 작성할 경우 total_amount의 값이 계산 결과 값으로 바뀌게 된다.
이를 방지하기 위해서는 .alias() 메서드를 통해 결과값을 저장할 컬럼명을 지정해주어야 한다.

shape: (5, 4)
┌─────────────┬───────────────────┬──────────────────┬──────────────┐
│ with_driver ┆ trip_distance - 1 ┆ trip_distance_km ┆ total_amount │
│ ---         ┆ ---               ┆ ---              ┆ ---          │
│ i64         ┆ f64               ┆ f64              ┆ f64          │
╞═════════════╪═══════════════════╪══════════════════╪══════════════╡
│ 2           ┆ -0.05             ┆ 1.528873         ┆ 15.052632    │
│ 2           ┆ 0.2               ┆ 1.931208         ┆ 14.083333    │
│ 3           ┆ 1.51              ┆ 4.0394434        ┆ 13.784861    │
│ 3           ┆ 1.9               ┆ 4.667086         ┆ 9.586207     │
│ 2           ┆ 0.53              ┆ 2.4622902        ┆ 9.934641     │
└─────────────┴───────────────────┴──────────────────┴──────────────┘
'''

pl_df.select(
					(pl.col('passenger_count') > 1).alias('people'),
					(pl.col('trip_distance') <= 1).alias('short_distance'),
					(pl.col('payment_type') != 'cash').alias('not_cash'),
					(pl.col('payment_type') == 'cash').alias('is_cash'),
					(
						(pl.col('total_amount') <= 20)
						& (pl.col('payment_type') == 'card')
					).alias('cheap_card'),
					(
						(pl.col('total_amount') > 20)
						& (pl.col('payment_type') == 'cash')
					).alias('expensive_or_cash')
	)
'''
논리연산을 진행할 경우 True or False 형태로 결과값이 리턴되어 컬럼이 구성된다.

shape: (5, 6)
┌────────┬────────────────┬──────────┬─────────┬────────────┬───────────────────┐
│ people ┆ short_distance ┆ not_cash ┆ is_cash ┆ cheap_card ┆ expensive_or_cash │
│ ---    ┆ ---            ┆ ---      ┆ ---     ┆ ---        ┆ ---               │
│ bool   ┆ bool           ┆ bool     ┆ bool    ┆ bool       ┆ bool              │
╞════════╪════════════════╪══════════╪═════════╪════════════╪═══════════════════╡
│ false  ┆ true           ┆ true     ┆ false   ┆ true       ┆ false             │
│ false  ┆ false          ┆ true     ┆ false   ┆ true       ┆ false             │
│ true   ┆ false          ┆ false    ┆ true    ┆ false      ┆ true              │
│ true   ┆ false          ┆ false    ┆ true    ┆ false      ┆ true              │
│ false  ┆ false          ┆ true     ┆ false   ┆ true       ┆ false             │
└────────┴────────────────┴──────────┴─────────┴────────────┴───────────────────┘
'''


# ------------------------------------------------------------
# df.filter()
# ------------------------------------------------------------
'''
조건에 해당하는 데이터만 추출하는 메서드
pandas에서 .loc 메서드를 통해 여러 조건을 적용하던 것을 polars에서는 filter 메서드로 표현할 수 있다.
조건 입력 방식은 위의 기본적인 연산 방법과 동일하게 pl.col() 메서드를 베이스로 작성하면 된다.
'''
pl_taxi_filtered = pl_taxi_df.filter(
													(pl.col('tpep_pickup_datetime') >= datetime.datetime(2024, 12, 1))
													& (pl.col('tpep_pickup_datetime') < datetime.datetime(2025, 1, 1))
	)
'''
tpep_pickup_datetime 값이 2024년 12월 1일 보다 크거나 같고, 2025년 1월 1일보다 작은 데이터만 추출하는 조건
'''


# ------------------------------------------------------------
# df.with_columns()
# ------------------------------------------------------------
'''
polars를 쓰면서 select와 함께 기본적으로 가장 많이 사용할 메서드로 컬럼을 선택하거나, 추가할 때 사용하는 기능이다.
select와 무슨 차이점이 있는가?
select의 경우 선택한 컬럼의 데이터만을 읽어오는 기능이다.
반면에 with_columns는 데이터 프레임을 구성하는 모든 컬럼들은 기본적으로 읽어들이며,
여기에 추가적으로 컬럼을 추가하거나, 컬럼에 연산, 작업 등을 하고 싶을 때 사용하는 메서드이다.

유의할 점은 위에서도 한 번 설명했던 내용인데,
with_columns를 사용해서 컬럼에 연산을 진행했을 때도 alias 등을 이용해 컬럼명을 지정해주지 않을 경우
새로운 컬럼이 생기는 것이 아니라 기존 컬럼의 값이 변경된다.
기존 컬럼의 값을 바꾸고 싶을 때는 굳이 기존 컬럼에 덮어 씌울 필요없이 연산만 진행하면 된다.

마찬가지로 결과 데이터프레임을 리턴하는 메서드로 결과값을 새로운 변수에 다시 할당해주어야 한다.
'''
print(pl_df.with_columns())
print(pl_df.with_columns('*'))

# 새 컬럼을 지정하는 방식
print(pl_df.with_columns(
									(pl.col('passenger_count')+1), # passenger_count 컬럼 자체의 값이 바뀐다.
									(pl.col('passenger_count')).alias('passenger_count_org'), # 기존 값을 남기고 싶어서 _org 컬럼으로 기존 값을 새로 생성
									(pl.col('passenger_count')+1).alias('passenger_count+1'), # +1한 값을 새로운 컬럼명으로 생성
									passenger_count_plus_1 = (pl.col('passenger_count')+1) # 컬럼을 생성하는 다른 방식
								)
)

'''
shape: (5, 5)
┌───────────┬─────────────────┬───────────────┬──────────────┬──────────────┐
│ vendor_id ┆ passenger_count ┆ trip_distance ┆ payment_type ┆ total_amount │
│ ---       ┆ ---             ┆ ---           ┆ ---          ┆ ---          │
│ str       ┆ i64             ┆ f64           ┆ str          ┆ f64          │
╞═══════════╪═════════════════╪═══════════════╪══════════════╪══════════════╡
│ A         ┆ 1               ┆ 0.95          ┆ card         ┆ 14.3         │
│ A         ┆ 1               ┆ 1.2           ┆ card         ┆ 16.9         │
│ B         ┆ 2               ┆ 2.51          ┆ cash         ┆ 34.6         │
│ B         ┆ 2               ┆ 2.9           ┆ cash         ┆ 27.8         │
│ B         ┆ 1               ┆ 1.53          ┆ card         ┆ 15.2         │
└───────────┴─────────────────┴───────────────┴──────────────┴──────────────┘

shape: (5, 8)
┌───────────┬────────────┬────────────┬────────────┬───────────┬───────────┬───────────┬───────────┐
│ vendor_id ┆ passenger_ ┆ trip_dista ┆ payment_ty ┆ total_amo ┆ passenger ┆ passenger ┆ passenger │
│ ---       ┆ count      ┆ nce        ┆ pe         ┆ unt       ┆ _count_or ┆ _count+1  ┆ _count_pl │
│ str       ┆ ---        ┆ ---        ┆ ---        ┆ ---       ┆ g         ┆ ---       ┆ us_1      │
│           ┆ i64        ┆ f64        ┆ str        ┆ f64       ┆ ---       ┆ i64       ┆ ---       │
│           ┆            ┆            ┆            ┆           ┆ i64       ┆           ┆ i64       │
╞═══════════╪════════════╪════════════╪════════════╪═══════════╪═══════════╪═══════════╪═══════════╡
│ A         ┆ 2          ┆ 0.95       ┆ card       ┆ 14.3      ┆ 1         ┆ 2         ┆ 2         │
│ A         ┆ 2          ┆ 1.2        ┆ card       ┆ 16.9      ┆ 1         ┆ 2         ┆ 2         │
│ B         ┆ 3          ┆ 2.51       ┆ cash       ┆ 34.6      ┆ 2         ┆ 3         ┆ 3         │
│ B         ┆ 3          ┆ 2.9        ┆ cash       ┆ 27.8      ┆ 2         ┆ 3         ┆ 3         │
│ B         ┆ 2          ┆ 1.53       ┆ card       ┆ 15.2      ┆ 1         ┆ 2         ┆ 2         │
└───────────┴────────────┴────────────┴────────────┴───────────┴───────────┴───────────┴───────────┘
'''


# ------------------------------------------------------------
# join(merge)
# how = 'inner', 'left', 'right', 'full', 'cross', 'semi', 'anti'
# ------------------------------------------------------------
'''
pandas의 merge, sql의 join의 기능
기본적인 방식 및 변수는 pandas와 동일하다.
df_a.join(df_b, on = [col1], how = 'inner', coalesce = None/True/False)
coalesce 변수의 경우 join에 사용된 컬럼에 대한 처리를 결정하는 변수이다.

menu = pl.DataFrame(
    {
        "item": ["coffee", "latte", "ade", "cake", "bread", "chocolate"],
        "type": ["beverage", "beverage", "beverage", "dessert", "dessert", "dessert"],
        "price": [3000, 4000, 5000, 6000, 7500, 4500]
    }
)

orders = pl.DataFrame(
    {
        "item": ["coffee", "ade", "coffee", "cake", "chocolate"],
        "number_of_orders": [1, 3, 7, 2, 5]
    }
)

shape: (6, 3)
┌───────────┬──────────┬───────┐
│ item      ┆ type     ┆ price │
│ ---       ┆ ---      ┆ ---   │
│ str       ┆ str      ┆ i64   │
╞═══════════╪══════════╪═══════╡
│ coffee    ┆ beverage ┆ 3000  │
│ latte     ┆ beverage ┆ 4000  │
│ ade       ┆ beverage ┆ 5000  │
│ cake      ┆ dessert  ┆ 6000  │
│ bread     ┆ dessert  ┆ 7500  │
│ chocolate ┆ dessert  ┆ 4500  │
└───────────┴──────────┴───────┘
shape: (5, 2)
┌───────────┬──────────────────┐
│ item      ┆ number_of_orders │
│ ---       ┆ ---              │
│ str       ┆ i64              │
╞═══════════╪══════════════════╡
│ coffee    ┆ 1                │
│ ade       ┆ 3                │
│ coffee    ┆ 7                │
│ cake      ┆ 2                │
│ chocolate ┆ 5                │
└───────────┴──────────────────┘
'''

print(menu.join(orders, on = ['item'], how = 'full', coalesce = True)) # join에 사용된 컬럼을 합쳐서 하나만 표시
print(menu.join(orders, on = ['item'], how = 'right', coalesce = False)) # join에 사용된 컬럼을 구분해서 표시
'''
shape: (7, 5)
┌───────────┬──────────┬───────┬────────────┬──────────────────┐
│ item      ┆ type     ┆ price ┆ item_right ┆ number_of_orders │
│ ---       ┆ ---      ┆ ---   ┆ ---        ┆ ---              │
│ str       ┆ str      ┆ i64   ┆ str        ┆ i64              │
╞═══════════╪══════════╪═══════╪════════════╪══════════════════╡
│ coffee    ┆ beverage ┆ 3000  ┆ coffee     ┆ 1                │
│ coffee    ┆ beverage ┆ 3000  ┆ coffee     ┆ 7                │
│ latte     ┆ beverage ┆ 4000  ┆ null       ┆ null             │
│ ade       ┆ beverage ┆ 5000  ┆ ade        ┆ 3                │
│ cake      ┆ dessert  ┆ 6000  ┆ cake       ┆ 2                │
│ bread     ┆ dessert  ┆ 7500  ┆ null       ┆ null             │
│ chocolate ┆ dessert  ┆ 4500  ┆ chocolate  ┆ 5                │
└───────────┴──────────┴───────┴────────────┴──────────────────┘

shape: (5, 5)
┌───────────┬──────────┬───────┬────────────┬──────────────────┐
│ item      ┆ type     ┆ price ┆ item_right ┆ number_of_orders │
│ ---       ┆ ---      ┆ ---   ┆ ---        ┆ ---              │
│ str       ┆ str      ┆ i64   ┆ str        ┆ i64              │
╞═══════════╪══════════╪═══════╪════════════╪══════════════════╡
│ coffee    ┆ beverage ┆ 3000  ┆ coffee     ┆ 1                │
│ ade       ┆ beverage ┆ 5000  ┆ ade        ┆ 3                │
│ coffee    ┆ beverage ┆ 3000  ┆ coffee     ┆ 7                │
│ cake      ┆ dessert  ┆ 6000  ┆ cake       ┆ 2                │
│ chocolate ┆ dessert  ┆ 4500  ┆ chocolate  ┆ 5                │
└───────────┴──────────┴───────┴────────────┴──────────────────┘

coalesce 변수의 default 값은 None으로 join에 따라 다르게 나타난다.
'''

print(menu.join(orders, on = ['item'], how = 'semi'))
print(menu.join(orders, on = ['item'], how = 'anti'))
'''
# semi 조인
베이스 데이터(left)에 대해서 join 컬럼에 대해서 서브 데이터(right)에 존재하는 데이터만 추출하는 작업
좀 더 이해가 쉽도록 표현하자면,
menu.filter(pl.col('item').is_in(orders['item']))

shape: (4, 3)
┌───────────┬──────────┬───────┐
│ item      ┆ type     ┆ price │
│ ---       ┆ ---      ┆ ---   │
│ str       ┆ str      ┆ i64   │
╞═══════════╪══════════╪═══════╡
│ coffee    ┆ beverage ┆ 3000  │
│ ade       ┆ beverage ┆ 5000  │
│ cake      ┆ dessert  ┆ 6000  │
│ chocolate ┆ dessert  ┆ 4500  │
└───────────┴──────────┴───────┘

# anti 조인
베이스 데이터에 대해서 join 컬럼에 대해서 서브 데이터에 존재하지 않는 데이터만 추출하는 작업
menu.filter(~pl.col('item').is_in(orders['item']))

shape: (2, 3)
┌───────┬──────────┬───────┐
│ item  ┆ type     ┆ price │
│ ---   ┆ ---      ┆ ---   │
│ str   ┆ str      ┆ i64   │
╞═══════╪══════════╪═══════╡
│ latte ┆ beverage ┆ 4000  │
│ bread ┆ dessert  ┆ 7500  │
└───────┴──────────┴───────┘
'''

# ------------------------------------------------------------
# group_by
# group_by 연산
# count, n_unique, max, min, mean, median, quantile(n), sum
# first, last - 각 그룹의 첫번째 값, 마지막 값 반환
# head(n), tail(n) - 각 그룹의 첫 n개, 마지막 n개 반환
# agg 메서드
# ------------------------------------------------------------
'''
기본적인 사용법은 판다스와 동일하다.
group_by() 메서드에 입력 값으로 그룹핑할 기준이 되는 컬럼을 입력하고,
뒤이어 체이닝으로 원하는 연산을 작성하면 된다.

그룹핑 연산을 진행할 경우, 모든 컬럼에 대해서 연산이 진행되며
집계할 수 없는 컬럼에 대해서는 null값을 반환한다.
따라서 원하는 값만 추출하기 위해서는 select를 통해서 원하는 컬럼 데이터만 선택한 후에
그룹핑 연산을 진행하는 것이 더 효율적이다.
'''
print(menu.group_by('type').sum())
print(menu.select('type', 'price').group_by('type').mean())
print(menu.select('type', 'price').group_by('type').max())
print(menu.select('type', 'price').group_by('type').head(3))
'''
shape: (2, 3)
┌──────────┬──────┬───────┐
│ type     ┆ item ┆ price │
│ ---      ┆ ---  ┆ ---   │
│ str      ┆ str  ┆ i64   │
╞══════════╪══════╪═══════╡
│ beverage ┆ null ┆ 12000 │
│ dessert  ┆ null ┆ 18000 │
└──────────┴──────┴───────┘

shape: (2, 2)
┌──────────┬────────┐
│ type     ┆ price  │
│ ---      ┆ ---    │
│ str      ┆ f64    │
╞══════════╪════════╡
│ beverage ┆ 4000.0 │
│ dessert  ┆ 6000.0 │
└──────────┴────────┘

shape: (2, 2)
┌──────────┬───────┐
│ type     ┆ price │
│ ---      ┆ ---   │
│ str      ┆ i64   │
╞══════════╪═══════╡
│ dessert  ┆ 7500  │
│ beverage ┆ 5000  │
└──────────┴───────┘

shape: (6, 2)
┌──────────┬───────┐
│ type     ┆ price │
│ ---      ┆ ---   │
│ str      ┆ i64   │
╞══════════╪═══════╡
│ dessert  ┆ 6000  │
│ dessert  ┆ 7500  │
│ dessert  ┆ 4500  │
│ beverage ┆ 3000  │
│ beverage ┆ 4000  │
│ beverage ┆ 5000  │
└──────────┴───────┘
'''

'''
agg 메서드를 활용할 경우 따로 사용할 데이터 컬럼을 select하는 과정이 필요 없다.
group_by에 사용된 컬럼과 agg 메서드에서 집계 연산하여 만든 컬럼들만 리턴되게 된다.
*join에 이어서 체이닝 연산으로 그룹핑 연산을 진행할 수 있다.
'''
menu.join(orders, on = ['item'], how = 'left').group_by(['type']).agg(
																								pl.col('number_of_orders').fill_null(0).sum().alias('total_orders'),
																								mean_orders = pl.col('number_of_orders').fill_null(0).mean()
																								# agg를 통해 컬럼을 생성하는 두가지 방법
	)
'''
shape: (2, 3)
┌──────────┬──────────────┬─────────────┐
│ type     ┆ total_orders ┆ mean_orders │
│ ---      ┆ ---          ┆ ---         │
│ str      ┆ i64          ┆ f64         │
╞══════════╪══════════════╪═════════════╡
│ beverage ┆ 11           ┆ 2.75        │
│ dessert  ┆ 7            ┆ 2.333333    │
└──────────┴──────────────┴─────────────┘
'''


# ------------------------------------------------------------
# df.shift(n, fill_value)
# pl.col().diff()
# ------------------------------------------------------------
'''
데이터를 shift하는 기능
n값을 따로 입력하지 않을 경우 기본적으로 다음 행으로 1칸 이동된다.
음수 값을 입력할 경우 반대 방향으로 이동된다.
데이터프레임 자체에 메서드를 적용할 경우 데이터 프레임 전체 행이 이동되며,
특정 컬럼에 대해서만 진행하고 싶을 경우 해당 컬럼에 대해서 메서드를 적용하면 된다.
원 컬럼을 유지하고 shift한 컬럼을 새로 추가하고 싶은 경우는
마찬가지로 with_columns 메서드를 활용하면 된다.

fill_value 변수를 이용하면, shift 후에 값이 없는 셀에 대해서 해당 값으로 채울 수 있다.

외에도 정말로 많은 기능들이 존재하지만 shift를 이용하는 것중에 가장 대표적인 목적인
이전 셀과의 차이를 계산하는 것은 따로 shift를 거치지 않아도 .diff() 메서드를 통해 계산이 가능하다.
'''

pl_df_shift = pl_df.with_columns(
											pl.col('total_amount').shift(1, fill_value = -999).alias('total_amount_shift_fill'),
											pl.col('total_amount').shift(1).alias('total_amount_shift')
										).select(
													pl.col(['total_amount', 'total_amount_shift_fill', 'total_amount_shift']),
													(pl.col('total_amount') - pl.col('total_amount_shift')).alias('shift_diff'),
													pl.col('total_amount').diff(1).alias('diff_method')
										)
print(pl_df_shift)
'''
shape: (5, 5)
┌──────────────┬─────────────────────────┬────────────────────┬────────────┬─────────────┐
│ total_amount ┆ total_amount_shift_fill ┆ total_amount_shift ┆ shift_diff ┆ diff_method │
│ ---          ┆ ---                     ┆ ---                ┆ ---        ┆ ---         │
│ f64          ┆ f64                     ┆ f64                ┆ f64        ┆ f64         │
╞══════════════╪═════════════════════════╪════════════════════╪════════════╪═════════════╡
│ 14.3         ┆ -999.0                  ┆ null               ┆ null       ┆ null        │
│ 16.9         ┆ 14.3                    ┆ 14.3               ┆ 2.6        ┆ 2.6         │
│ 34.6         ┆ 16.9                    ┆ 16.9               ┆ 17.7       ┆ 17.7        │
│ 27.8         ┆ 34.6                    ┆ 34.6               ┆ -6.8       ┆ -6.8        │
│ 15.2         ┆ 27.8                    ┆ 27.8               ┆ -12.6      ┆ -12.6       │
└──────────────┴─────────────────────────┴────────────────────┴────────────┴─────────────┘
diff 메서드를 활용한 결과와 shift후에 연산을 진행한 결과를 비교해보자.
'''


# ------------------------------------------------------------
# .str.contains(pattern)
# .str.replace_all(pattern, replace_string)
# .str.extract_all(pattern)
# ------------------------------------------------------------
'''
판다스와 마찬가지로 str 타입 데이터에 대해서, 검색, 교체, 추출 등을 진행할 수 있다.
정규표현식 사용도 가능하며,
해당 기능은 Rust를 통해 벡터 연산 진행되기 때문에 속도가 매우 빠르다.
contains, replace_all, extract_all 모두 정규표현식 적용이 가능하며,
체이닝을 통해 한 컬럼에 여러 표현을 적용하는 것이 가능하다.

map_elements를 이용할 경우 행 하나하나 지정 함수가 적용되는 것이기 때문에 속도 측면에서 매우 비효율적이다.
'''
df = pl.DataFrame({
					    "html_text": [
									        "<p>Hello &amp; welcome!</p>",
									        "<div>Error: 404 &lt;Not Found&gt;</div>",
									        "<span>Price: $100 &amp; tax</span>",
									        "<script>alert('xss')</script><b>Bold</b>"
									    ],
					    "contact_info": [
										        "Email: alice@example.com, bob@test.org",
										        "Phone: 010-1234-5678",
										        "No contact here",
										        "Emails: charlie@domain.com; Phone: 02-8765-4321"
										    ],
					    "message": [
								        "foo bar baz foo",
								        "no match here",
								        "foo, foo, foo",
								        ""
								    ]
})
print(df)
'''
shape: (4, 3)
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────┐
│ html_text                       ┆ contact_info                    ┆ message         │
│ ---                             ┆ ---                             ┆ ---             │
│ str                             ┆ str                             ┆ str             │
╞═════════════════════════════════╪═════════════════════════════════╪═════════════════╡
│ <p>Hello &amp; welcome!</p>     ┆ Email: alice@example.com, bob@… ┆ foo bar baz foo │
│ <div>Error: 404 &lt;Not Found&… ┆ Phone: 010-1234-5678            ┆ no match here   │
│ <span>Price: $100 &amp; tax</s… ┆ No contact here                 ┆ foo, foo, foo   │
│ <script>alert('xss')</script><… ┆ Emails: charlie@domain.com; Ph… ┆                 │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────┘
'''

# contains
df_contains = df.select(
								pl.col('message'),
								pl.col('message')
								.str.contains('foo')
								.alias('has_foo')
							)

# replace_all
df_replace = df.select(
								pl.col('html_text'),
								pl.col('html_text')
								.str.replace_all(r"<[^>]+>", "", literal = False) #정규표현식 사용
								.str.replace_all("&amp;", "&", literal = True) #정규표현식이 아니라 문자열 그대로 사용
								.str.replace_all("&lt;", "<", literal = False)
								.str.replace_all("&gt;", ">", literal = False)
								.alias('clean_html')
							)

# extract_all
df_extract = df.select(
								pl.col('contact_info'),
								pl.col('contact_info')
								.str.extract_all(r"[\w\.-]+@[\w\.-]+")
								.alias('emails'),
								pl.col('contact_info')
								.str.extract_all(r"[0-9]{2,3}-[0-9]{3,4}-[0-9]{4}")
								.alias('phones')
							)

print(df_contains)
print(df_replace)
print(df_extract)
'''
shape: (4, 2)
┌─────────────────┬─────────┐
│ message         ┆ has_foo │
│ ---             ┆ ---     │
│ str             ┆ bool    │
╞═════════════════╪═════════╡
│ foo bar baz foo ┆ true    │
│ no match here   ┆ false   │
│ foo, foo, foo   ┆ true    │
│                 ┆ false   │
└─────────────────┴─────────┘

shape: (4, 2)
┌─────────────────────────────────┬────────────────────────┐
│ html_text                       ┆ clean_html             │
│ ---                             ┆ ---                    │
│ str                             ┆ str                    │
╞═════════════════════════════════╪════════════════════════╡
│ <p>Hello &amp; welcome!</p>     ┆ Hello & welcome!       │
│ <div>Error: 404 &lt;Not Found&… ┆ Error: 404 <Not Found> │
│ <span>Price: $100 &amp; tax</s… ┆ Price: $100 & tax      │
│ <script>alert('xss')</script><… ┆ alert('xss')Bold       │
└─────────────────────────────────┴────────────────────────┘


shape: (4, 3)
┌─────────────────────────────────┬─────────────────────────────────┬───────────────────┐
│ contact_info                    ┆ emails                          ┆ phones            │
│ ---                             ┆ ---                             ┆ ---               │
│ str                             ┆ list[str]                       ┆ list[str]         │
╞═════════════════════════════════╪═════════════════════════════════╪═══════════════════╡
│ Email: alice@example.com, bob@… ┆ ["alice@example.com", "bob@tes… ┆ []                │
│ Phone: 010-1234-5678            ┆ []                              ┆ ["010-1234-5678"] │
│ No contact here                 ┆ []                              ┆ []                │
│ Emails: charlie@domain.com; Ph… ┆ ["charlie@domain.com"]          ┆ ["02-8765-4321"]  │
└─────────────────────────────────┴─────────────────────────────────┴───────────────────┘
'''

# ------------------------------------------------------------
# pl.when(조건1).then(결과1).when(조건2).then(결과2)....when(조건N).then(결과N).otherwise(나머지).alias()
# pl.case().when(조건1, 결과1).when(조건2, 결과2)....when(조건N, 결과N).otherwise(나머지).alias()
# ------------------------------------------------------------
'''
SQL의 CASE문과 비슷한 형태로 사용할 수 있다.
여러 조건을 적용할 때도 간단하게 체이닝을 통해 연결만 해주면 되기 때문에 사용이 간편하다.
'''
df.with_columns(
						pl
						.when(pl.col('contact_info').str.contains('[0-9]{2,3}-[0-9]{3,4}-[0-9]{4}'))
						.then(pl.lit('phone'))

						.when(pl.col('contact_info').str.contains('[a-zA-Z\.-]+@[a-zA-Z\.-]+'))
						.then(pl.lit('email'))

						.when(pl.col('contact_info').str.contains('[0-9]{2,3}-[0-9]{3,4}-[0-9]{4}')
						     & pl.col('contact_info').str.contains('[a-zA-Z\.-]+@[a-zA-Z\.-]+'))
						.then(pl.lit('both'))
						.otherwise(pl.lit('nothing'))
						.alias('contact_method')
					)
'''
shape: (4, 4)
┌───────────────────────────────┬───────────────────────────────┬─────────────────┬────────────────┐
│ html_text                     ┆ contact_info                  ┆ message         ┆ contact_method │
│ ---                           ┆ ---                           ┆ ---             ┆ ---            │
│ str                           ┆ str                           ┆ str             ┆ str            │
╞═══════════════════════════════╪═══════════════════════════════╪═════════════════╪════════════════╡
│ <p>Hello &amp; welcome!</p>   ┆ Email: alice@example.com,     ┆ foo bar baz foo ┆ email          │
│                               ┆ bob@…                         ┆                 ┆                │
│ <div>Error: 404 &lt;Not       ┆ Phone: 010-1234-5678          ┆ no match here   ┆ phone          │
│ Found&…                       ┆                               ┆                 ┆                │
│ <span>Price: $100 &amp;       ┆ No contact here               ┆ foo, foo, foo   ┆ nothing        │
│ tax</s…                       ┆                               ┆                 ┆                │
│ <script>alert('xss')</script> ┆ Emails: charlie@domain.com;   ┆                 ┆ phone          │
│ <…                            ┆ Ph…                           ┆                 ┆                │
└───────────────────────────────┴───────────────────────────────┴─────────────────┴────────────────┘
'''