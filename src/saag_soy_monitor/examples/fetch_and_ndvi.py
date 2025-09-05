import json, argparse, os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bbox', type=str, required=False, help='minx,miny,maxx,maxy')
    parser.add_argument('--crs', type=str, default='EPSG:4326')
    parser.add_argument('--start', type=str, required=False)
    parser.add_argument('--end', type=str, required=False)
    args = parser.parse_args()
    print('Prototype stub running with:', vars(args))
    # Placeholders for actual data fetch & NDVI processing

if __name__ == '__main__':
    main()
