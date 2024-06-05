# SMALL SUMMARY
for max_workers in 1 5 10 20
do
    python main.py -m $max_workers -n 100 -t 100
done

# MEDIUM SUMMARY
for max_workers in 1 5 10 20
do
    python main.py -m $max_workers -n 100 -t 500
done

# BIG SUMMARY
for max_workers in 1 5 10 20
do
    python main.py -m $max_workers -n 100 -t 1000
done