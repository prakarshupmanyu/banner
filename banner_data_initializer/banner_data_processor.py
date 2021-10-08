from pyspark.sql import SparkSession
from pyspark.sql.window import Window
import pyspark.sql.functions as f
from pyspark.sql.functions import desc

spark = SparkSession.builder.appName("BannerApp").getOrCreate()
for i in range(1, 5):
    clicks_file = "/data/csv/" + str(i) + "/clicks_" + str(i) + ".csv"
    impressions_file = "/data/csv/" + str(i) + "/impressions_" + str(i) + ".csv"
    conversions_file = "/data/csv/" + str(i) + "/conversions_" + str(i) + ".csv"
    clicks_df = spark.read.option("header", True).csv(clicks_file).dropDuplicates()
    impressions_df = spark.read.option("header", True).csv(impressions_file).dropDuplicates()
    conversions_df = spark.read.option("header", True).csv(conversions_file).dropDuplicates()

    clicks_df.registerTempTable("clicks")
    conversions_df.registerTempTable("conversions")
    impressions_df.registerTempTable("impressions")

    campaign_banners_with_conversion_df = \
        spark.sql("select count(distinct banner_id) as X, campaign_id "
                  "from clicks cl inner join conversions co "
                  "on cl.click_id = co.click_id "
                  "where co.revenue > 0.0 "
                  "group by cl.campaign_id")

    banner_performance_df = spark.sql("select i.campaign_id, i.banner_id, total_revenue, total_clicks "
                                      "from impressions i left join ("
                                      "select campaign_id, banner_id, "
                                      "sum(revenue) as total_revenue, count(cl.click_id) as total_clicks "
                                      "from clicks cl left join conversions co "
                                      "on cl.click_id = co.click_id "
                                      "group by cl.campaign_id, cl.banner_id) temp "
                                      "on i.campaign_id = temp.campaign_id and i.banner_id = temp.banner_id "
                                      "group by i.campaign_id, i.banner_id, total_revenue, total_clicks")\
        .fillna(0, subset=['total_revenue', 'total_clicks'])

    w = Window.partitionBy(banner_performance_df.campaign_id).orderBy(desc("total_revenue"), desc("total_clicks"))

    ordered_banner_df = banner_performance_df.withColumn("order", f.row_number().over(w)).filter("order <= 10")
    final_df = ordered_banner_df.join(campaign_banners_with_conversion_df,
                                      ordered_banner_df.campaign_id == campaign_banners_with_conversion_df.campaign_id,
                                      "left")\
        .drop(campaign_banners_with_conversion_df.campaign_id)\
        .fillna(0, subset=['X'])

    campaign_banner_table = "q" + str(i) + "_campaign_banners"
    final_df.write.format('jdbc').options(
        url='jdbc:mysql://mysql:3306/banner',
        driver='com.mysql.cj.jdbc.Driver',
        dbtable=campaign_banner_table,
        user='user',
        password='password').mode('overwrite').save()

spark.stop()
print("DONE!!!")
