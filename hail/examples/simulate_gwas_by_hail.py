from pyspark.sql import SparkSession
import hail as hl
from sparkhpc import sparkjob
import sys
import os

# Connect to existing Spark cluster
sj_list = sparkjob.sparkjob().current_clusters()
if not sj_list:
    print("ERROR: No running Spark cluster found!")
    print("Please start a cluster first with: sparkcluster start <ncores>")
    sys.exit(1)

cluster = sj_list[0]
master_url = cluster.master_url()
print(f"Connecting to Spark cluster at {master_url}")

# Get Hail JAR path
hail_dir = os.path.dirname(hl.__file__)
hail_jar = os.path.join(hail_dir, 'backend', 'hail-all-spark.jar')
print(f"Using Hail JAR: {hail_jar}")

# Connect to the existing cluster with Hail JAR and serialization configuration
spark = (SparkSession.builder
    .master(master_url)
    .appName("GWAS-Hail")
    .config("spark.jars", hail_jar)
    .config("spark.driver.extraClassPath", hail_jar)
    .config("spark.executor.extraClassPath", f"./hail-all-spark.jar:{hail_jar}")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.kryo.registrator", "is.hail.kryo.HailKryoRegistrator")
    .getOrCreate())

print(f"Spark version: {spark.version}")
print(f"Spark master: {spark.sparkContext.master}")
print(f"Spark serializer: {spark.sparkContext.getConf().get('spark.serializer')}")

print("\nInitializing Hail...")
hl.init(sc=spark.sparkContext)
print("✓ Hail initialized successfully!")

# Submit jobs to simulate the data
mt = hl.balding_nichols_model(n_populations=3,
                              n_samples=500,
                              n_variants=500_000,
                              n_partitions=32)
mt = mt.annotate_cols(drinks_coffee = hl.rand_bool(0.33))
gwas = hl.linear_regression_rows(y=mt.drinks_coffee,
                                 x=mt.GT.n_alt_alleles(),
                                 covariates=[1.0])
gwas.order_by(gwas.p_value).show(25)