#!/usr/bin/env python
"""
Calculate Pi using Monte Carlo method in PySpark
Connects to existing Spark cluster started via sparkcluster CLI

Usage:
    1. Start cluster: sparkcluster start 4 --partition main --spark-home $SPARK_HOME
    2. Run this script: python examples/pi_counter.py
    3. Stop cluster: kill the sparkcluster process or wait for walltime
"""
import sys
import os

# Add sparkhpc to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sparkhpc'))

from sparkhpc import sparkjob
from pyspark import SparkConf, SparkContext
from random import random
from math import pi as math_pi
import time

def inside(p):
    """Check if a random point (x, y) is inside the unit circle"""
    x, y = random(), random()
    return x*x + y*y <= 1

def main():
    print(f"\n{'='*70}")
    print(f"PySpark Pi Calculation - Monte Carlo Method")
    print(f"{'='*70}")
    
    # Get the running cluster (cluster 0)
    try:
        sj = sparkjob.sparkjob(clusterid=0)
    except Exception as e:
        print(f" Error: Could not find running cluster!")
        print(f"  Make sure to start cluster first:")
        print(f"  $ sparkcluster start 4 --partition main --spark-home $SPARK_HOME")
        print(f"  Error details: {e}")
        sys.exit(1)
    
    print(f"\nConnecting to Spark cluster...")
    print(f"  Cluster ID: 0")
    print(f"  Job ID: {sj.jobid}")
    
    # Wait for master to be available
    print(f"\nWaiting for Spark Master (timeout: 60 seconds)...")
    deadline = time.time() + 60
    master_url = None
    
    while time.time() < deadline:
        try:
            master_url = sj.master_url()
            if master_url:
                print(f" Master URL: {master_url}")
                break
        except:
            pass
        time.sleep(0.5)
    
    if not master_url:
        print(" Could not connect to Spark master!")
        print(f"  Verify cluster is running:")
        print(f"  $ squeue")
        print(f"  Check logs:")
        print(f"  $ tail spark_master.out")
        sys.exit(1)
    
    ui_url = sj.master_ui()
    print(f" Master UI: {ui_url}")
    
    # Create SparkContext and connect to the master
    print(f"\nCreating SparkContext...")
    conf = SparkConf().setMaster(master_url).setAppName("PiCalculator")
    sc = SparkContext(conf=conf)
    
    try:
        # Calculate pi
        num_samples = 100000000  # 100 million samples
        num_partitions = 4
        
        print(f"\nCalculating Pi with {num_samples:,} samples across {num_partitions} partitions...")
        print(f"This will take 15-20 seconds...\n")
        
        # Create RDD and calculate pi
        start_time = time.time()
        count = sc.parallelize(range(0, num_samples), num_partitions).filter(lambda _: inside(_)).count()
        elapsed_time = time.time() - start_time
        
        # Calculate result
        pi_estimate = 4.0 * count / num_samples
        error = abs(pi_estimate - math_pi)
        accuracy = (1 - error/math_pi) * 100
        
        print(f"{'='*70}")
        print(f"RESULTS:")
        print(f"{'='*70}")
        print(f"Pi estimated value: {pi_estimate:.10f}")
        print(f"Actual Pi value:    {math_pi:.10f}")
        print(f"Error:              {error:.10f}")
        print(f"Accuracy:           {accuracy:.6f}%")
        print(f"Execution time:     {elapsed_time:.2f} seconds")
        print(f"Points inside:      {count:,} / {num_samples:,}")
        print(f"{'='*70}\n")
        
    finally:
        print(f"Stopping SparkContext...")
        sc.stop()
        print(f" Job completed successfully!")

if __name__ == "__main__":
    main()
