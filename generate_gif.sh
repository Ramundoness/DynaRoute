while getopts n:d:v:t: flag
do
    case "${flag}" in
        n) num_nodes=${OPTARG};;
        d) density=${OPTARG};;
        v) volatility=${OPTARG};;
        t) topology=${OPTARG};;
    esac
done
echo "Num Nodes: $num_nodes";
echo "Density: $density";
echo "Volatility: $volatility";
echo "Topology: $topology";
echo

echo "Deleting plots/*.png"
rm plots/*.png
echo

echo "Running script: python3 main.py --graphics --num_nodes=$num_nodes --topology=$topology --density=$density --volatility=$volatility"
python3 main.py --graphics --num_nodes=$num_nodes --topology=$topology --density=$density --volatility=$volatility

echo "GIF-ifying... -- it's pronounced GIF"
gifski -o gifs/${topology}-n${num_nodes}-d${density}-v${volatility}.gif plots/*-*.png

