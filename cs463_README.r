Cody A. Ruhlen 
UIN 01332300
CS 463: 16868 - Fall 2025
Instructor: Dr. J. Takeshita
Old Dominion University

************************************************************************************************************************************************************************************************************************
CIPHER PERFORMANCE COMPARISONS
************************************************************************************************************************************************************************************************************************

This project benchmarks the runtime, memory usage, and efficiency of four symmetric ciphers across multiple message sizes.  The ciphers are:

-AES-128 (ECB): Implemented using PyCryptodome (Crypto.Cipher.AES, ECB mode)
-Ascon-128: AEAD cipher, winner of NIST lightweight crypto competition
-Simon: Lightweight block cipher (reference Python implementation)
-Speck: Lightweight block cipher (reference Python implementation)

This script measures two variables, time to encrypt and decrypt and peak memory usage during the operation.  The ratio of these variables is calculated to determine the efficiency of each respective cipher.  

The results of the tests are printed for each cipher within each message size.  The total results are listed at the end and the script produces plots to visualize the performance of each cipher using Matplotlib.

************************************************************************************************************************************************************************************************************************
DEPENDENCIES
************************************************************************************************************************************************************************************************************************

Install the required libraries using:
    pip install pycryptodome ascon matplotlib

Python implementations for Simon and Speck are included in this repository as 
    simon.py
    speck.py

************************************************************************************************************************************************************************************************************************
METHODOLOGY
************************************************************************************************************************************************************************************************************************

A test is initiated for each size in the message_sizes list.  The test runs all four cipher functions.

Each cipher function runs an encryption and decrytion test the amount of times listed for the variable {runs}.  

The first run of each cipher is a ghost run that is not measured or listed in the results.  This is to avoid first run inlflation while Python initializes resources.  

Each cipher function lists the remaining runs and results and appends each result to a [totals] list.  Once the runs are finished, these totals are averaged for each size and totaled at the end.  

To determine the efficiency of each cipher, the program divides memory usage by time used.  This measures the amount of memory needed to run the cipher for a second.  Lower efficiency ratios are better because it shows the ciphers are less "memory hungry".  

Finally, the total results are listed at the end and the ciphers are ranked by efficiency ratios.  

Plots are generated to visualise the results.  

************************************************************************************************************************************************************************************************************************
OUTPUT
************************************************************************************************************************************************************************************************************************

The script prints:
    -Message size
        -Cipher name
        -Run x
        -Time Used
        -Memory Used
        -Average Time
        -Average Memory
        -Efficiency Ratios
        (repeated for each cipher)
            -Winners tables with sorted results
                -Average Time
                -Average Memory
                -Efficiency Ratios
    (repeated for each message size)
    -Total values
        -Sum of results from all runs for each cipher
    -Final rankings table
    -Cipher Runtime vs Message Size plot
    -Cipher Memory Usage vs Message Size Plot
    -Cipher Efficiency Ratio vs Message Size plot

Results print as follows:

64 Byte Tests

AES-128: 64 bytes
Run 1
  Time 0.000192 sec | Mem 0.005340 MB
Run 2
  Time 0.000232 sec | Mem 0.005316 MB
Run 3
  Time 0.000228 sec | Mem 0.005284 MB
Run 4
  Time 0.000226 sec | Mem 0.004988 MB
Run 5
  Time 0.000258 sec | Mem 0.005708 MB
----------------------------------------------------------------------------------
AES-128 64 byte | Average Time: 0.000227 sec | Average Memory Used: 0.005327 MB

...

----------------------------------------------------------------------------------
64 byte Winners sorted by Efficiency Ratio
----------------------------------------------------------------------------------
Rank   Cipher          Time Used   Memory Used      Efficiency Ratio
----------------------------------------------------------------------------------
1      Ascon        0.010172 sec   0.001518 MB       0.149201 MB/sec
2      Simon        0.013048 sec   0.005331 MB       0.408612 MB/sec
3      Speck        0.004269 sec   0.003543 MB       0.829960 MB/sec
4      AES-128      0.000227 sec   0.005327 MB      23.438929 MB/sec

...

**********************************************************************************
Cipher Totals & Efficiency Ratios (across all sizes, combined runs)
**********************************************************************************
Cipher            Time Used        Memory Used          Efficiency Ratio
------------------------------------------------------------------------
AES-128        0.004299 sec        0.017367 MB           4.039589 MB/sec
Ascon          2.749738 sec        0.023626 MB           0.008592 MB/sec
Simon          4.431484 sec        0.042968 MB           0.009696 MB/sec
Speck          1.654129 sec        0.042963 MB           0.025973 MB/sec

==================================================================================
Efficiency Rankings
==================================================================================

Rank   Cipher                Efficiency Ratio
---------------------------------------------
1      Ascon                  0.008592 MB/sec
2      Simon                  0.009696 MB/sec
3      Speck                  0.025973 MB/sec
4      AES-128                4.039589 MB/sec

************************************************************************************************************************************************************************************************************************
USAGE
************************************************************************************************************************************************************************************************************************
    
Run the script  
    python cs463project.py

************************************************************************************************************************************************************************************************************************
CONFIGURATION
************************************************************************************************************************************************************************************************************************

The following variables may be changed at the top of the script:
    -message_sizes = [64, 256, 1024, 4096]
    -runs = 6
    -key_aes = b"thequickbrownfox"
    -key_ascon = b"thequickbrownfox"
    -key_simon = int.from_bytes(b"thequickbrownfox"[:8], "big")
    -key_speck = int.from_bytes(b"thequickbrownfox"[:8], "big")
    -nonce = b"andthreelazydogs"
    -block_size_bytes = 8
    -def the_message(size):
        return (b"jumpedoverazebra" * ((size // 16) + 1))[:size]

************************************************************************************************************************************************************************************************************************
NOTES
************************************************************************************************************************************************************************************************************************

tracemalloc was incorporated because I was not getting results with memory_usage.  The differences in these tests were so small, the memory given by memory_usage was all zeroes.

As mentioned before, a ghost run was implemented due to first iteration inflation, particularly with AES-128 under te 64 byte tests.  The ghost run was implemented for all ciphers to ensure fairness.  

************************************************************************************************************************************************************************************************************************
DISCUSSION
************************************************************************************************************************************************************************************************************************

This program was designed to help determine which cipher methods would be most appropriate for environments with low resources, such as those of IoT devices.  After running the program several times, I have concluded 
the Ascon-128 cipher is an excellent choice for resource restricted environments.  

AES-128 is by far the fastest method, but it demands so much memory for every second it runs.  For this test, the time used is less two hundredths of a second at most, but as the payload size rises, the cipher will 
take longer and put strain on a low resource device.  The Efficiency Ratio for AES-128 when run in Jupyter Notebook was consistently around 4 MB/sec.  This is exponentially larger than the others, which were consistently
under 0.03 MB/sec.

Simon and Speck each use a lot of memory, especially with larger message sizes.  They also take more time to encrypt and decrypt, so the strain on a device is spread over time.  Simon most frequently came in second,
usually clocking around 0.01 MB/sec, while Speck consistently came in third, around 0.025 MB/sec.

Ascon-128 is the happy medium between time and memory.  While AES is resource heavy and Simon and Speck take their time, Ascon-128 splits the two.  It was consistently the winner, usually finding a ratio of 0.008 MB/sec.  

A copy of  test run in Jupyter Notebook will also be included in this repository. 
