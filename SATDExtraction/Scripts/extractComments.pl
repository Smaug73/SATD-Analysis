#! /usr/bin/perl
use strict;
use warnings;

my $srcmlPath=$ARGV[0];
my $filePath = $ARGV[1];

my $command=$srcmlPath."/srcml ".$filePath;
my $execute=`$command`;

my @lines=split("\n",$execute);
chomp(@lines);

my $nlines=$#lines;
my $counter=0;
my $start=$counter;

my %comments=();
my $found=0;

while (($counter<=$nlines) && (!$found)){
	my $line=$lines[$counter];
	if ($line=~/<class><specifier>/){
		$found=1;
	}else{
		$counter++;
	}
}

$counter++;

while ($counter<=$nlines){
	my $comment="";
	my $line=$lines[$counter];

	if ($line=~/<comment type="line"/){
		my $remaining=$';
		if ($remaining=~/>(.*)<\/comment>/){
			my $starting = $counter;
			$comment=$1;
			$counter++;
			$line=$lines[$counter];
			while ($line=~/<comment type="line/){
				$remaining=$';
				if($remaining=~/>(.*)<\/comment>/){
					$comment = $comment." ".$1;	
				}
				$counter++;
				$line=$lines[$counter];
			}
			$counter--;	
			$comments{$starting}=$comment;
		}
	}
	if ($line=~/<comment type="block"/){
		if ($line=~/>(.*)<\/comment>/){
			$comments{$counter}=$1;
		}else{
			my $remaining=$';
			if ($remaining=~/\">/){
				$comment=$';
				$start=$counter;
				$counter++;
				$line = $lines[$counter];
				while (!($line=~/<\/comment>/) and ($counter<=$nlines)){
					$comment = $comment." ".$line;
					$counter++;
					$line = $lines[$counter];
				}
				if ($line=~/<\/comment>/){
					$comment = $comment." ".$`;
				}
				$comments{$start}=$comment;
			}
		}
	}
	$counter++;
}

my @keys = keys (%comments);
for my $key (@keys){
	print $key." ".$comments{$key}."\n";
}

