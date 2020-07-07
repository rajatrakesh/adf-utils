from __future__ import print_function
from azure.storage.blob import BlockBlobService
from azure.storage.blob.models import Blob, BlobProperties
from io import BytesIO
import pyarrow as pa
import pyarrow.parquet as pq
import sys

def get_pandas_dataframe_from_parquet_on_blob(blob_service, container_name, blob_name):
    """ Get a dataframe from Parquet file on blob storage """
    byte_stream = BytesIO()
    try:
        blob_service.get_blob_to_stream(
            container_name=container_name, blob_name=blob_name, stream=byte_stream
        )
        df = pq.read_table(source=byte_stream).to_pandas()
    finally:
        byte_stream.close()
    return df

def write_pandas_dataframe_to_blob(blob_service, df, container_name, blob_name):
    """ Write Pandas dataframe to blob storage """
    buffer = BytesIO()
    df.to_parquet(buffer)
    blob_service.create_blob_from_bytes(
        container_name=container_name, blob_name=blob_name, blob=buffer.getvalue()
    )
    
def get_blob_size(blob_service, container_name, blob_name):
    """ Get the size of the blob object to calculate compression factor """
    length = blob_service.get_blob_properties(container_name, blob_name).properties.content_length
    return length

def main():
    kilobytes = 1024
    megabytes = kilobytes * 1024
    chunkSize = int(10 * megabytes)
    compressFactor = 10
    blobSize = 0
    dataFrameSize = 0
    newFileSize = 0
	
    storageAccountName = ""
    storageKey         = ""
    containerName      = ""
    outputFolder       = ""
    blobName 		   = ""
	
    #print('Number of arguments:', str(len(sys.argv)))
    #print(len(sys.argv))
    #print('Argument List:')
    #print(str(sys.argv))
    
    storageAccountName = sys.argv[1]
    storageKey = sys.argv[2]
    containerName = sys.argv[3]
    outputFolder = sys.argv[4]
    blobName = sys.argv[5]
    chunkSize = int(sys.argv[6])
    chunkSize = int(chunkSize * megabytes)

    blobService = BlockBlobService(account_name=storageAccountName,
                                   account_key=storageKey
                                   )
    
    blobSize = get_blob_size(blobService, containerName, blobName)
    
    # Read from blob using pyarrow
    rdf = get_pandas_dataframe_from_parquet_on_blob(blobService, containerName, blobName)
    
    # Identify the size of memory used by DataFrame
    dataFrameSize = rdf.memory_usage(index=True).sum()
    
    # Idenfity the compression factor by comparing dataframe size and blob object size
    compressFactor = dataFrameSize / blobSize


    # Derive the number of files to split the new parquet into, based on the total size of dataframe
    splits = int((dataFrameSize / (chunkSize * compressFactor)) + 1)
    
    # Identify the number of records in the dataframe to then subset on rowcounts
    numofrecords = len(rdf)
    rowstart = 0
    rowincrement = round(numofrecords / splits) - 1
    rowend = rowincrement
    
    # Output for debugging the properties and split criteria
    print(f"Total records in the original file: {numofrecords:,}")
    print(f"Total Size of the Blog File : {blobName} is {blobSize:,} bytes or {(blobSize / megabytes):.2f} MB")
    print(f"The files will be split in chunks of upto {(chunkSize / megabytes):.2f} MB similar splits")
    print(f"Total memory in use by DataFrame: {dataFrameSize:,} bytes or {(dataFrameSize / megabytes):.2f} MB")
    print(f"The compression factor being used to split files is: {compressFactor:.2f}")
    print(f"The resulting parquet will be split into {splits} files")
    print(f"Total Records written per file will be: {rowincrement:,} ")


    x = 1
    for x in range(splits):
        filename = 'part%04d' %x + '.parq'
        if x == splits - 1:
            rowend = numofrecords
        write_pandas_dataframe_to_blob(blobService, rdf.iloc[rowstart:rowend], containerName, (outputFolder + filename))
        rowstart = rowend + 1
        rowend += rowincrement
        xdf =  get_pandas_dataframe_from_parquet_on_blob(blobService, containerName, (outputFolder + filename))
        newFileSize = get_blob_size(blobService, containerName, (outputFolder + filename))
        print(f"Validating the # of records written in file: {filename} is {len(xdf):,} Size: {(newFileSize / megabytes):.2f} MB")
    exit(0)

main()