# Azure Batch Integration in Azure Data Factory

This tutorial explores a use case where large-scale datasets need to be processed in ADF (Azure Data Factory) in a scheduled manner while driving the entire transformation pipeline from ADF. It also provides a working example to test this concept by deploying a sample use-case. 

If you are new to Batch (Azure Batch) and ADF, you would still be able to explore this use-case by following along the instructions in this article, to learn more about both and how they work seamlessly together. 

### Azure Batch

Azure Batch is extremely useful to quickly deploy and scale high-performance computing applications efficiently in the cloud. You can schedule compute-intensive workloads to run on a collection of Virtual Machines (VMs). It is also possible to setup autoscaling to scale compute resources, depending on your workload requirements. 

Workloads can be executed on demand, or on a schedule and it is extremely easy to deploy, as we will see in the use case, without having to manage individual VMs, virtual networks etc. For Additional details on Batch, please refer to:

* [Basics of Batch](https://docs.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview)
* [Batch Feature Overview](https://docs.microsoft.com/en-us/azure/batch/batch-service-workflow-features)
* [Batch Documentation](https://docs.microsoft.com/en-us/azure/batch/batch-service-workflow-features)

### Azure Data Factory

Data Factory can help create managed data pipelines that move data from on-premises and cloud data stores to a centralized data store. For instance,  you can use Data Factory to process/transform data by using services such as Azure HDInsight and Azure Machine Learning. You also can schedule data pipelines to run in a scheduled manner (for example, hourly, daily, and weekly). You can monitor and manage the pipelines at a glance to identify issues and take action.

Additional details on Data Factory are available here:

* [Data Factor Introduction](https://docs.microsoft.com/en-us/azure/data-factory/v1/data-factory-introduction)
* [Tutorial: Building Data Pipelines with Data Factory](https://docs.microsoft.com/en-us/azure/data-factory/v1/data-factory-build-your-first-pipeline)



### Azure Data Factory and Azure Batch 

Azure Data Factory has two type of activities:

* [Data Movement](https://docs.microsoft.com/en-us/azure/data-factory/copy-activity-overview) : To move data between [supported sources](https://docs.microsoft.com/en-us/azure/data-factory/copy-activity-overview#supported-data-stores-and-formats) and [sink data stores](https://docs.microsoft.com/en-us/azure/data-factory/copy-activity-overview#supported-data-stores-and-formats)
* [Data Transformation](https://docs.microsoft.com/en-us/azure/data-factory/transform-data): To transform data during various compute services such as Azure HDInsigh, Azure Batch, Azure Machine learning etc. 

In addition to the above, there are often use-cases that are not directly supported by ADF, for example where you may need to transform the data in a certain way. For such operations, ADF provides an option for **Custom activity** where you can build your own transformation and processing logic and integrate this in the ADF pipeline as part of the flow. This Custom Activity would then run your code in the compute environment provided by Azure Batch, over a pool of virtual machines. 



### Azure Batch Architecture

![Azure Batch Architecture](./images/azure-batch/01_batch_overview.jpg)

### Use Case

I recently had a use case where there were data was being extracted out of SQL Managed Instance  on Azure. The data files were processed into parquet and multiple tables (of various size) could be written out in every extraction process. These parquet files, were of transactional in nature (staging) and hence were not partitioned as a) the skew could change every day 2) uneven distribution of data. 

The target of these files expected them to be up to 100MB and equally split, to be able to effectively load data in parallel for performance.

Hence, there was a need to pre-process and translate these files to fit the above requirements.  We are going to explore this use case with Azure Data Factory and Azure Batch.  



### Tutorial

We are going to setup everything step by step, and as long as you have an Azure account you would be able to follow along. In case you don't have one, you could sign up for a **free Azure account, that gives you 12 months of free services** [here](https://azure.microsoft.com/en-us/free/) and **Monthly Azure Credits for Visual Studio subscribers [here](https://azure.microsoft.com/en-us/pricing/member-offers/credit-for-visual-studio-subscribers/)**. We will go through the following steps:

* [Setup Storage](#setup-storage)
* [Setup Azure Data Factory](#setup-azure-data-factory)
* [Create a simple pipeline in Data Factory](#create-a-simple-pipeline-in-data-factory)
* [Setup Azure Batch](#setup-azure-batch)
* Configure Azure Batch with Data Factory
* Add a custom activity to pipeline
* Create a python script
* Execute the pipeline
* Monitor pipeline execution in Data Factory
* Monitor Azure Batch



## Setup Storage

Once you have setup a resource group, the first thing we will deploy would be a storage account. This is where our source and target data will reside.

1. ![Setup Storage Account](./images/azure-batch/02_setup_storage_ac.jpg)

Configure 'Basics' as follows. 

![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_1.jpg)

During the lab, we would setup folders, so enable 'Hierarchical Namespace'.

![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_1a.jpg)

Click 'Create'.

![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_2.jpg)

Once 'Storage Account' is setup, go to resource. We will set up 2 containers now. 

Click 'Containers'

![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_3.jpg)



Let's setup 2 containers: `filestoreage` as the source/target for the files that we will process and `batchstorage` for files that will be used by Azure Batch later. 

![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_4.jpg)



![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_5.jpg)

![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_6.jpg)

Navigate to `filestorage` and create 3 directories: `input`, `source`, `target`.

![Setup Storage Account](./images/azure-batch/02_setup_storage_ac_7.jpg)

## Setup Azure Data Factory

Now we need to add an ADF instance to our resource group. Click ''+Add New' under 'Analytics' categrory.

![Setup Storage Account](./images/azure-batch/03_setup_adf_1.jpg)

Provide values as below, and click 'Create'.

![Setup Storage Account](./images/azure-batch/03_setup_adf_2.jpg)



Once the deployment is successful, go to Data Factory Overview screen and click on 'Author and Monitor' to launch the console.

![Setup Storage Account](./images/azure-batch/03_setup_adf_3.jpg)

The following screen will show up.

![Setup Storage Account](./images/azure-batch/03_setup_adf_4.jpg)



## Create a Simple Pipeline in Data Factory

Let's create a simple pipeline to source some data that we will use for testing and place it in the appropriate folder. 

## Setup Azure Batch

For setting up Azure Batch, there are two things that we need to configure:

* Setup a Batch Account
* Create a pool of compute nodes

### Setup a Batch Account

Click 'Create a Resource' and then select 'Batch Service' from 'Compute' category.

![Setup Storage Account](./images/azure-batch/04_setup_batch_1.jpg)



References:

[Using custom activities in Azure Data Factory Pipeline](https://docs.microsoft.com/en-us/azure/data-factory/transform-data-using-dotnet-custom-activity)

[Process large-scale datasets by using Data Factory and Batch](https://docs.microsoft.com/en-us/azure/data-factory/v1/data-factory-data-processing-using-batch)

[Tutorial : Run python scripts through Azure Dat Factory using Azure Batch](https://docs.microsoft.com/en-us/azure/batch/tutorial-run-python-batch-azure-data-factory)

​	