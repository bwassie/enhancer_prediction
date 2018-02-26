import os, sys
import pandas as pd
import argparse

def change_length(peak,name,dist,shorten):
	df = pd.read_csv(peak,sep="\t", header=None)
	df["peak_dist"] = df.iloc[:,2] - df.iloc[:,1]
	print(df["peak_dist"].describe())
	df.loc[df["peak_dist"] < dist,2] = df[df["peak_dist"] < dist].iloc[:,2] +  (dist - df[df["peak_dist"] < dist]["peak_dist"])/2.0
	df.loc[df["peak_dist"] < dist, 1] = df[df["peak_dist"] < dist].iloc[:,1] -  (dist - df[df["peak_dist"] < dist]["peak_dist"])/2.0
	if shorten:
		df.loc[df["peak_dist"] > dist,2] = df[df["peak_dist"] > dist].iloc[:,2] -  (dist - df[df["peak_dist"] > dist]["peak_dist"]).abs()/2.0
		df.loc[df["peak_dist"] > dist, 1] = df[df["peak_dist"] > dist].iloc[:,1] +  (dist - df[df["peak_dist"] > dist]["peak_dist"]).abs()/2.0
	df.loc[:,1] = df.loc[:,1].astype(int)
	df.loc[:,2] = df.loc[:,2].astype(int)
	df = df[(df.iloc[:,1] >= 0)& (df.iloc[:,2] >= 2000)]
	df["peak_dist"] = df.iloc[:,2] - df.iloc[:,1]
	print(df["peak_dist"].describe())
	print(df.head())
	df.loc[:,[0,1,2]].to_csv(name,sep="\t",index=False,header=False)

def merge(name,name2, dist):
	os.system("source /home/bwassie/.bashrc")
	os.system("bedtools sort -i {} | bedtools merge -d {} -i - > {}".format(name,dist,name2))
	
def post_process(name,name2):
	os.system('''awk -F"\t" '{{$(NF+1)="PEAK"++i;}}1' OFS="\t" {}  | awk -F"\t" '{{$(NF+1)="10";}}1' OFS="\t" |awk -F"\t" '{{$(NF+1)=".";}}1' OFS="\t" > {}'''.format(name,name2))
	
def main():
	parser = argparse.ArgumentParser(description='Change peak widths. By default, this will extend peaks to specified length and merge overlapping peaks')
	parser.add_argument("peak",help="Peak file to modify")
	parser.add_argument("dist",default=1000,help="Distance to extend peaks. Default is 1kb. If --fix is not set, peaks shorter than dist will be extended to dist.")
	parser.add_argument("--fix",action='store_true',help="Indicate if you want to fix peak widths. This will shorten peaks longer than dist to be equal to dist. If --extend is not set, this will merge peaks first and then fix peaks to specified size")
	parser.add_argument("--extend",action='store_true',help="Indicate if you want to extend peaks only and not merge")
	args = parser.parse_args()
	peak = args.peak
	dist = int(args.dist)
	fix = args.fix
	extend = args.extend
	
	name,ext = os.path.splitext(os.path.basename(peak))
	name=os.path.basename(peak).replace(ext,"_{}bp.bed".format(str(dist)))
	name2=name.replace(".bed","_merged.bed")
	
	
	if fix:
		if extend:
			name3=name.replace(".bed","_extend_fixed.bed")
			change_length(peak,name,dist,fix)
			post_process(name,name3)
		else:
			name3=name.replace(".bed","_merged_extend_fixed.bed")
			merge(peak,name,dist)
			change_length(name,name2,dist,fix)
			post_process(name2,name3)			
	else:
		if extend:
			name3=name.replace(".bed","_extend.bed")
			change_length(peak,name,dist,fix)
			post_process(name,name3)
		else:
			name3=name.replace(".bed","_extend_merged.bed")
			change_length(name,name2,dist,fix)
			merge(name2,name3,dist)
			post_process(name2,name3)	
			
	os.system("rm {}".format(name))
	os.system("rm {}".format(name2))
	
if __name__ == "__main__":
	main()
