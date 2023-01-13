#! /usr/bin/perl
use strict;
use warnings;

my $filePath=$ARGV[0];

my $srcmlPath=$ARGV[1];

my $command=$srcmlPath."/srcml ".$filePath;
my $execute=`$command`;

my @allLines = split("\n",$execute);

my $id=0;

my $start = $id;
while ($id<=$#allLines){
	my $signature="";
	my $line = $allLines[$id];
	if ($line =~/\<constructor\>/ || $line=~/\<function\>/){
		$line=$';
		$start = $id;
		while (($line!~/\<block\>/) && ($id<=$#allLines)){
				$id++;		
				$line = $line."".$allLines[$id];
		}
		if ($line=~/\<block\>/){$line = $`;}
		while($line=~/(\<\/?[a-zA-Z\_\s\"\=]+\>)/){
				$line=~s/$1//;
		}
		$line =~s/\s+/ /g;
		$line =~s/^\s//g;
		$line =~s/\{//g;
		##angular brackets
		$line =~s/\&lt\;/\</g;
		$line =~s/\&gt\;/\>/g;
		$signature = $line;

		
		$signature=~tr{\n}{ };
		$signature=~s/\s+\(/\(/;

		$signature =~/([\w\.]+\([^\(]+)$/;
		my $mname=$1;
		if($mname=~/\s+throws/)
  		{
    		$mname=$`;
			
  		}

		$signature=$mname;

		$id++;
		if($id<=$#allLines) {$line = $allLines[$id]};
		while(($id<=$#allLines) && ($line!~/\<\/function\>/) && ($line!~/\<\/constructor\>/)){
			$id++;
			$line = $allLines[$id];
		}
		print $signature." ".$start."--".$id."\n";
	}
	
	$id++;
}
