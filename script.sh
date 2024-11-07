#!/bin/bash

delays=(10 50 100)
losses=(0.1 0.5 1.0)
variants=("reno" "cubic")

# Set MTU to 1500 bytes
sudo ifconfig lo mtu 1500

for variant in "${variants[@]}"; do
    # Set the TCP congestion control variant
    sudo sysctl -w net.ipv4.tcp_congestion_control=$variant
    echo "Using TCP congestion control variant: $variant"
    
    for delay in "${delays[@]}"; do
        for loss in "${losses[@]}"; do
            echo "Running tests for delay: ${delay}ms, loss: ${loss}%, variant: $variant"
            
            # Set up `tc` rules for delay, loss, and bandwidth using `htb`
            sudo tc qdisc add dev lo root handle 1: htb default 10
            sudo tc class add dev lo parent 1: classid 1:10 htb rate 100mbit ceil 100mbit quantum 1500
            sudo tc qdisc add dev lo parent 1:10 handle 10: netem delay ${delay}ms loss ${loss}%
            
            # Run 20 trials for each configuration
            for i in {1..20}; do
                # Print the trial number
                echo "Trial $i for ${variant}, delay ${delay}ms, loss ${loss}%"
                
                # Run iperf3 with a fixed amount of data (20M) and log output
                iperf3 -c 127.0.0.1 -n 20MB -f m > output_${variant}${delay}${loss}.txt
                
                # Extract throughput and log it
                grep "sender" output_${variant}${delay}${loss}.txt | awk '{print $7 " " $8}' >> results_${variant}${delay}${loss}.csv
            done

            # Delete `tc` rules to reset before the next configuration
            sudo tc qdisc del dev lo root
            echo "Completed tests for delay: ${delay}ms, loss: ${loss}%, variant: $variant"
        done
    done
done

echo "All tests completed."
