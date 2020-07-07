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
* [Setup Azure Batch](#setup-azure-batch)
* [Create a simple pipeline in Data Factory](#create-a-simple-pipeline-in-data-factory)
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



## Setup Azure Batch

For setting up Azure Batch, there are two things that we need to configure:

* Setup a Batch Account
* Create a pool of compute nodes

### Setup a Batch Account

Click 'Create a Resource' and then select 'Batch Service' from 'Compute' category.

![Setup Storage Account](./images/azure-batch/04_setup_batch_1.jpg)

Configure options as follows, and keep all other settings to default.  Click 'Create'.

![Setup Storage Account](./images/azure-batch/04_setup_batch_2.jpg)

Once the resource is deployed, open the resource to navigate to the Batch Account.

![Setup Storage Account](./images/azure-batch/04_setup_batch_3.jpg)

### Create  a Pool of Compute Nodes

Now that our batch account is setup, we would need to add compute where the actual processing will happen. This can be done in two ways:

* Adding Pool from Azure Portal
* Adding Pool from Batch Explorer

#### Adding Pool from Azure Portal (Optional)

The easiest option is to add a compute directly from the Portal. While it is very easy and straightforward to use, at the same time not all options are shown. If you use the Batch Explorer Client, you have many more options available. For this lab, we will use setup Pools using **Batch Explorer**. However, we will look at both options. *You can choose to not go through this section, since we will not be using this pool during the lab.*

To create a pool from Azure Portal, click 'Pools' in the 'Azure Batch' resource, and then click Add.

![Setup Storage Account](./images/azure-batch/04_setup_batch_4.jpg)

Setup the pool with settings below:

![Setup Storage Account](./images/azure-batch/04_setup_batch_5a.jpg)

We will add just **1** dedicated node for this example. 

![Setup Storage Account](./images/azure-batch/04_setup_batch_5b.jpg)

**Note**: If you plan to launch a customized image with components pre-installed, then you can also leverage the [custom-image functionality](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/capture-image). 

Once the Pool is successfully deployed, you will be able to see the status in the Pools screen. 

![Setup Storage Account](./images/azure-batch/04_setup_batch_6.jpg)

Since we wouldn't be using this pool for the lab, you can delete it, to save resources. Right click on the Pool name, and select 'Delete'.

#### Adding Pool from Batch Explorer

To deploy a Pool from Batch Explorer, you must first **install Batch Explorer** on your local machine. This can be done from the Batch Account > Overview Page. Click 'Batch Explorer Option'.

![Setup Storage Account](./images/azure-batch/04_setup_batch_7.jpg)

Once you have downloaded and installed, open Batch Explorer' locally. It would require your 'credentials' and you'll be able to connect to your Azure Account. You will see all the Batch Accounts deployed in your Azure Account. 

![Setup Storage Account](./images/azure-batch/04_setup_batch_8.jpg)

Select your Batch Account in which you want to create a Pool. Then click 'Pools' on the left menu bar. Click '+' to add Pools.

Setup the options as below. We will use only 1 task per node and use only 1 node. 

![Setup Storage Account](./images/azure-batch/04_setup_batch_9.jpg)



Next we will choose the type of image that we want use for our compute instance. As you will see, there are a lot more options available in Batch Explorer, as compared to Portal. We will use 'Dsvm Windows' under Data Science, and choose 'Standard_f2s_v2' as the virtual machine size. 

![Setup Storage Account](./images/azure-batch/04_setup_batch_10.jpg)

During the lab, we will be using python to execute transformations on data. For that, let's install a few custom libraries to the compute resource. Since we will set these up in the 'Start Task', these will apply automatically to any clones to additional nodes that we deploy. 

Click 'Add a start task' under 'Start Task'.

![Setup Storage Account](./images/azure-batch/04_setup_batch_11.jpg)



In the 'Command Line' enter `cmd /c "pip install pandas dask pyarrow"`

Keep the 'User identity' as 'Pool User'.

![Setup Storage Account](./images/azure-batch/04_setup_batch_12.jpg)

Click 'Save and Close'.

The  pool will deploy, and once successfully deployed, it will be visible under 'Pools' on the left sub menu.

![Setup Storage Account](./images/azure-batch/04_setup_batch_13.jpg)



## Create a Simple Pipeline in Data Factory

Let's create a simple pipeline to source some data that we will use for testing and place it in the appropriate folder. 

Open Azure Data Factory per earlier instructions, and click on 'Create Pipeline'.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_1.jpg)

In this lab, we will use existing parquet files for airline dataset available [here](https://www.transtats.bts.gov/Tables.asp?DB_ID=120). While the data available at the source is substantial (1.4gb compressed), for this lab you can also download a sample parquet file (15MB) from the repo directory `sample-data`. 

*If you would like to simulate multiple files, then you can upload this file after renaming it.*

In a live use-case, this data could be an export out of a data warehouse/mart or OLTP, or could even be a output of an IOT process. It is beyond the scope of this lab, to create a pipeline for simulating this. Hence, we will start with an assumption that a parquet input file is available to us. 

Upload this file in your `filestorage` container, in the `input` directory.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_2.jpg)

Once the file is uploaded, we will setup a pipeline in Data Factory.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_3.jpg)

In this lab, we will:

* **Copy Data** from `input` folder to `source` folder using 'Copy Data'.

In the next section, we will then:

* Split this file into equal number of files, on the basis of parameters using **Custom Batch Service**.
* Parameterize this process, so it can work on multiple files across different folders, using the same code.

To create the first pipeline, drag and drop the 'Copy Data'

![Setup Storage Account](./images/azure-batch/05_create_pipeline_4.jpg)



Change the name of the pipeline to 'CopyParquet' from 'pipeline1'.

In this pipeline, we will setup our `input` folder as the source, and `source` as the target. This is to also ensure that our original sample file is not modified,  especially if you run this pipeline multiple times. 

Change the name in the 'General' section to 'CopyFile'.

Click Source. Click '+ New' and select 'Azure Blob Storage' from the menu, as the source of our data. As you can see, ADF is able to pick up data from a variety of sources. 

![Setup Storage Account](./images/azure-batch/05_create_pipeline_5.jpg)

Click 'Continue'. From the next screen, choose 'Parquet' as the format.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_6.jpg)

Click 'Continue'.

In the next screen, we need to setup a 'Linked Service' for the source location. 

Change the name from 'Parquet1' to 'SourceParquet'. Click 'Linked Service' and 'Add New'.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_7.jpg)

In the next screen, we will setup the credentials to access our source location.

Change the name from 'AzureBlobStorage1' to 'SourceBlobStorage'.

For authentication method, various options are available. We will choose 'Account Key'.

You would need the following details:

* Storage Account Name
* Storage Account Key
* Endpoint suffix

For this lab, we will use 'Azure Subscription', instead of providing all of these manually.

Setup the options as below, and 'Test connection.'

![Setup Storage Account](./images/azure-batch/05_create_pipeline_8.jpg)

In the next screen, we will define the path for the file(s) location.

You can either manually type the path, or use the button to select it. 

![Setup Storage Account](./images/azure-batch/05_create_pipeline_9.jpg)

In this scenario, we want all files of .parq extension to be picked up automatically, you can do so by editing wildcards as a selection criteria. You can modify this under the 'Source' tab.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_9a.jpg)

Similarly, setup the 'Sink'. 

Under 'Sink', 'Sink Dataset', click '+ New'.

Since our target is also an Azure Blob Storage, select that from options, and the output is again going to be a parquet file.

Give the name 'TargetParquet' and create another New 'Linked Service'.

Name it 'TargetBlobStorage' and follow the same process as above to setup the link. Test Connection. Create.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_10.jpg)



Now choose the `source` folder as your destination. Select 'None' under 'Import schema'. We are choosing `source` as this will be our source folder for the transformation process.

Click Ok. 

Let's name our target file as 'NewFile.parq'.

Click 'Sink' > Open 'TargetParquet' and enter the filename. There are option for parameterization, but we'll skip that for now.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_12.jpg)



We want to setup this pipeline in a way that it will merge multiple files into a single output file. Under 'Sink', select 'Merge Files' as the 'Copy  Behaviour'.

Let's validate that there are no issues in our pipeline. 

Click 'Validate All' on the top left of the screen. Once it succeeds, click 'Publish all' to commit changes. This will deploy all changes to Data Factory. Once you get a alert 'Publishing Completed', our pipeline is ready.

Before we start this, let's validate that there is no data in either source or target directory.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_13.jpg)



To execute this pipeline, click 'Add Trigger' > 'Trigger Now'. Click Ok.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_14.jpg)

In a few mins, you'll get a notification that the pipeline has succeeded.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_15.jpg)

The file 'NewFile.parq' has been create in the `source` folder.

![Setup Storage Account](./images/azure-batch/05_create_pipeline_16.jpg)



References:

[Using custom activities in Azure Data Factory Pipeline](https://docs.microsoft.com/en-us/azure/data-factory/transform-data-using-dotnet-custom-activity)

[Process large-scale datasets by using Data Factory and Batch](https://docs.microsoft.com/en-us/azure/data-factory/v1/data-factory-data-processing-using-batch)

[Tutorial : Run python scripts through Azure Dat Factory using Azure Batch](https://docs.microsoft.com/en-us/azure/batch/tutorial-run-python-batch-azure-data-factory)

​	