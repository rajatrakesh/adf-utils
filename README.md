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





References:

[Using custom activities in Azure Data Factory Pipeline](https://docs.microsoft.com/en-us/azure/data-factory/transform-data-using-dotnet-custom-activity)

[Process large-scale datasets by using Data Factory and Batch](https://docs.microsoft.com/en-us/azure/data-factory/v1/data-factory-data-processing-using-batch)

[Tutorial : Run python scripts through Azure Dat Factory using Azure Batch](https://docs.microsoft.com/en-us/azure/batch/tutorial-run-python-batch-azure-data-factory)

​	