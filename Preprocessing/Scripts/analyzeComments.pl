#! /usr/bin/perl
use strict;
#use warnings;
use Text::Levenshtein qw(distance);

sub mapping{
	my @methods = @{$_[0]};
	my %mappingMethods=();
	for my $m(@methods){
		if ($m=~/\s(\d+\-\-\d+)/){
			$mappingMethods{$1}=$`;
		}
	}
	return \%mappingMethods;
}

sub computedistance{
	my $comment = $_[0];
	my @values = @{$_[1]};

	my $clen = length($comment);
	for my $v (@values){
		my $dist = distance($comment, $v);
		my $perc = ($dist * 100)/$clen;
		if ($perc <= 5){
			return 1;
		}
	}
	return 0;
}

sub searchBeginEnd{
	my $signature=$_[0];
	my %mapping = %{$_[1]};

	for my $m (keys(%mapping)){
		if ($signature eq $mapping{$m}){
			return $m;
		}
	}
	return "0--0";
}

sub areEquals{
	my $comment = $_[0];
	my @array = @{$_[1]};

	for my $a (@array){
		if ($a eq $comment){
			return 1;
		}
	}
	return 0;
}

sub linkCommentsAndMethods{
	my @comments=@{$_[0]};
	my @methods=@{$_[1]};

	my %mapping=();
	my %comments_map=();
	my %methods_map=();

	for my $k (@comments){
		if ($k=~/(^\d+)\s/){
			$comments_map{$1}=$';
		}
	}

	for my $k (@methods){
		if ($k=~/(\d+)\-\-(\d+)/){
			$methods_map{$1}=$2;
		}
	}

	for my $c (keys(%comments_map)){
		my $is_inline = 0;
		for my $m (keys(%methods_map)){
			if (($c > $m) && ($c < $methods_map{$m})){
				my $key_value=$c." ".$comments_map{$c};
				my $value = $m."--".$methods_map{$m};
				$mapping{$key_value}=$value;
				$is_inline = 1;
			}
		}

		if (!$is_inline){ 
			my $pointer=1000000; 
			my $diff = -1; 
			for my $m (keys(%methods_map)){
				$diff = $m-$c;
				if (($diff > 0) && ($m < $pointer)){
					$pointer=$m;		
				}
			}
			if ($pointer!=1000000){
				my $key_value=$c." ".$comments_map{$c};
				my $value = $pointer."--".$methods_map{$pointer};
				$mapping{$key_value}=$value;
			}
		}
	}

	return \%mapping;
}

sub replaceIndexLinesAndFormat{
	my @values = @{$_[0]};
	my @modified_values = ();

	for my $v (@values){
		$v=~s/^\d+ //g;
		$v=~s/(\r|\t|\n)/ /g;
		$v=~s/\s+/ /g;
		push @modified_values, $v;
	}
	return \@modified_values;
}

sub createSubsets{
	my %mappings=%{$_[0]};
	my %subsets=();

	for my $m (keys(%mappings)){
		if (!exists($subsets{$mappings{$m}})){
			my @value=();
			push @value, $m;
			$subsets{$mappings{$m}}=\@value;
		}else{
			my @value=@{$subsets{$mappings{$m}}};
			push @value, $m;
			$subsets{$mappings{$m}}=\@value;
		}
	}
	return \%subsets;
}

my $beginning = localtime();

my $projectPath=$ARGV[0];
my $basePath=$ARGV[1];

my $srcmlPath=$ARGV[2];
my $pathexsigscript = $ARGV[3];
my $pathexcommentsscript = $ARGV[4];
my $detectorjarPath = $ARGV[5];

chdir($projectPath);

my $command = "git log --format=format:%H";
my $execute=`$command`;

my @commits=split("\n",$execute);
chomp(@commits);

print ("Commit,File,TypeOfChange,Signature,Begin--End,Comment,CommentType\n");

for my $commit (@commits){
	chdir($projectPath);

	#$commit = "7c79a748a5626149606608742a0c4e958c01cb96";
	#$commit="46eab6b1e90d9dd6c4f7898f41ff4a05ef68b0da";
#	$commit = "a8a9e645e7c5ac3d5354580b9eb22df67acba520";
	$command = "git show --name-status --oneline ".$commit;
	$execute=`$command`;

	my @summary = split("\n", $execute);
	chomp(@summary);

	my @modified =();
	my @removed =();
	my @added =();

	for my $line (@summary){
		if ($line=~/^M/){
			my $fileName = $';
			$fileName=~s/\s//g;
			if ($fileName=~/\.java\z/){
				push @modified, $fileName;
			}
		}elsif ($line=~/^A/){
			my $fileName = $';
			$fileName=~s/\s//g;
			if ($fileName=~/\.java\z/){
				push @added, $fileName;
			}			
		}elsif ($line=~/^D/){
			my $fileName = $';
			$fileName=~s/\s//g;
			if ($fileName=~/\.java\z/){
				push @removed, $fileName;
			}			
		}
	}
	
	## deal with modified files
	if (!scalar @modified == 0){
		##access the parent commit 
		$command = "git log --pretty=%P -n 1 ".$commit;
		my $parent=`$command`;
		chomp($parent);
		$command = "git checkout ".$commit;
		$execute = `$command`;

		for my $mfile (@modified){
			my $filePath=$projectPath."".$mfile;
			if (-e $filePath){
				$command = "cp ".$filePath." ".$basePath."temporary/current/";
				$execute = `$command`;
			}
		}

		$command = "git checkout ".$parent;
		$execute = `$command`;

		for my $mfile (@modified){
			my $filePath=$projectPath."".$mfile;
			if (-e $filePath){
				$command = "cp ".$filePath." ".$basePath."temporary/previous/";
				$execute = `$command`;
			}
		}

		for my $mfile (@modified){
			my @fields=split("\/", $mfile);
			chomp(@fields);
			chdir ($basePath);

			my $current = $basePath."temporary/current/".$fields[$#fields];
			my $previous = $basePath."temporary/previous/".$fields[$#fields];
			
			if ((-e $current) && (-e $previous)){
				$command = "perl -w ".$pathexsigscript." ".$current." ".$srcmlPath;
				$execute = `$command`;
				my @methodsCurrent = split("\n",$execute);
				chomp(@methodsCurrent);
				$command = "perl -w ".$pathexsigscript." ".$previous." ".$srcmlPath;
				$execute = `$command`;
				my @methodsPrevious = split("\n",$execute);
				chomp(@methodsPrevious);

				$command = "perl -w ".$pathexcommentsscript." ".$srcmlPath." ".$current;
				$execute = `$command`;
				my @commentsCurrent = split("\n",$execute);
				chomp(@commentsCurrent);

				$command = "perl -w ".$pathexcommentsscript." ".$srcmlPath." ".$previous;
				$execute = `$command`;
				my @commentsPrevious = split("\n",$execute);
				chomp(@commentsPrevious);

				my %mappingCurrent=%{linkCommentsAndMethods(\@commentsCurrent,\@methodsCurrent)};
				my %mappingPrevious=%{linkCommentsAndMethods(\@commentsPrevious,\@methodsPrevious)};

				my %subsetCurrent = %{createSubsets(\%mappingCurrent, \@methodsCurrent)};
				my %subsetPrevious = %{createSubsets(\%mappingPrevious, \@methodsPrevious)};

				my %mmethodsCurrent = %{mapping(\@methodsCurrent)};
				my %mmethodsPrevious = %{mapping(\@methodsPrevious)};								


				my %subsetCurrentSignature = ();
				for my $s (keys(%subsetCurrent)){
					if (exists($mmethodsCurrent{$s})){
						my @values = @{$subsetCurrent{$s}};
						$subsetCurrentSignature{$mmethodsCurrent{$s}}=\@values;
					}
				}

				my %subsetPreviousSignature = ();
				for my $s (keys(%subsetPrevious)){
					if (exists($mmethodsPrevious{$s})){
						my @values = @{$subsetPrevious{$s}};
						$subsetPreviousSignature{$mmethodsPrevious{$s}}=\@values;
					}
				}

				## compare the two different subsets of methods and related comments
				for my $s (keys(%subsetCurrentSignature)){
					if (!exists($subsetPreviousSignature{$s})){
						## Added Method
						my @values = @{$subsetCurrentSignature{$s}};
						for my $v (@values){
							my $com = $v;
							$v=~s/^\d+\s//g;
							$com=~s/\(/ /g;
							$com=~s/\)/ /g;
							if ($com=~/\b(TODO|FIXME|HACK|XXX)\b/){
								$v=~s/,/ /g;
								$v=~s/\s+/ /g;
								my $beginEnd = searchBeginEnd($s, \%mmethodsCurrent);		
								print $commit.",".$mfile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
							}else{
								$command = "java -jar ".$detectorjarPath." test -c".$com;
								$execute =`$command`;
								$v=~s/\,/ /g;
								$v=~s/\s+/ /g;
								my $beginEnd = searchBeginEnd($s, \%mmethodsCurrent);		
								if ($execute=~/Not SATD/){
									print $commit.",".$mfile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",Not SATD\n";
								}else{
									print $commit.",".$mfile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
								}
							}
						}
					}else{
						## Modified Method
						my @valuesCurrent = @{$subsetCurrentSignature{$s}};
						my @valuesPrevious = @{$subsetPreviousSignature{$s}};
						
						@valuesCurrent = @{replaceIndexLinesAndFormat(\@valuesCurrent)};
						@valuesPrevious = @{replaceIndexLinesAndFormat(\@valuesPrevious)};

						## TODO compute similarity and define a treshold

						for my $v (@valuesCurrent){
							if (!(areEquals($v, \@valuesPrevious))){
								$v=~s/^\d+\s//g;	
								my $com = $v;
								$com=~s/\(/ /g;
								$com=~s/\)/ /g;
								if ($com=~/\b(TODO|FIXME|HACK|XXX)\b/){
									$v=~s/,/ /g;
									$v=~s/\s+/ /g;
									my $beginEnd = searchBeginEnd($s, \%mmethodsCurrent);		
									print $commit.",".$mfile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
								}else{
									$command = "java -jar ".$detectorjarPath." test -c".$com;
									$execute =`$command`;
									$v=~s/\,/ /g;
									$v=~s/\s+/ /g;
									my $beginEnd = searchBeginEnd($s, \%mmethodsCurrent);		
									if ($execute=~/Not SATD/){
										print $commit.",".$mfile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",Not SATD\n";
									}else{
										print $commit.",".$mfile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
									}
								}

							}
						}

						for my $v (@valuesPrevious){
							if (!(areEquals($v, \@valuesCurrent))){
								my $com = $v;
								$v=~s/^\d+\s//g;
								$com =~s/\(/ /g;
								$com =~s/\)/ /g;	
								if ($com=~/\b(TODO|FIXME|HACK|XXX)\b/){
									$v=~s/,/ /g;
									$v=~s/\s+/ /g;
									my $beginEnd = searchBeginEnd($s, \%mmethodsPrevious);		
									print $commit.",".$mfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
								}else{
									$command = "java -jar ".$detectorjarPath." test -c".$com;
									$execute =`$command`;
									$v=~s/\,/ /g;
									$v=~s/\s+/ /g;
									my $beginEnd = searchBeginEnd($s, \%mmethodsPrevious);		
									if ($execute=~/Not SATD/){
										print $commit.",".$mfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",Not SATD\n";
									}else{
										print $commit.",".$mfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
									}
								}

							}
						}

					}
				}

				for my $s (keys(%subsetPreviousSignature)){
					if (!exists($subsetCurrentSignature{$s})){
						## Removed Methods
						my @values = @{$subsetPreviousSignature{$s}};
						for my $v (@values){
							my $com = $v;
							$v=~s/^\d+\s//g;
							$com =~s/\(/ /g;
							$com =~s/\)/ /g;
							if ($com=~/\b(TODO|FIXME|HACK|XXX)\b/){
								$v=~s/,/ /g;
								$v=~s/\s+/ /g;
								my $beginEnd = searchBeginEnd($s, \%mmethodsPrevious);		
								print $commit.",".$mfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
							}else{
								$command = "java -jar ".$detectorjarPath." test -c".$com;
								$execute =`$command`;
								$v=~s/,/ /g;
								$v=~s/\s+/ /g;
								my $beginEnd = searchBeginEnd($s, \%mmethodsPrevious);		
								if ($execute=~/Not SATD/){
									print $commit.",".$mfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",Not SATD\n";
								}else{
									print $commit.",".$mfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
								}
							}
						}
					}
				}



			}

		}

		$command = "rm ".$basePath."temporary/current/\*";
		$execute = `$command`;

		$command = "rm ".$basePath."temporary/previous/\*";
		$execute = `$command`;

	}

	chdir($projectPath);

	if (!scalar @added == 0){
		$command = "git checkout ".$commit;
		$execute = `$command`;

		for my $afile (@added){
			my $filePath=$projectPath."".$afile;
			if (-e $filePath){
				$command = "cp ".$filePath." ".$basePath."temporary/current/";
				$execute = `$command`;
			}
		}

		for my $afile (@added){
			my @fields=split("\/", $afile);
			chomp(@fields);
			chdir ($basePath);

			my $current = $basePath."temporary/current/".$fields[$#fields];

			if (-e $current){
				$command = "perl -w ".$pathexsigscript." ".$current." ".$srcmlPath;
				$execute = `$command`;
				my @methods = split("\n",$execute);
				chomp(@methods);

				$command = "perl -w ".$pathexcommentsscript." ".$srcmlPath." ".$current;
				$execute = `$command`;
				my @comments = split("\n",$execute);
				chomp(@comments);

				my %mapping=%{linkCommentsAndMethods(\@comments,\@methods)};
				my %subset = %{createSubsets(\%mapping, \@methods)};
				my %mmethods = %{mapping(\@methods)};

				my %subsetSignature = ();
				for my $s (keys(%subset)){
					if (exists($mmethods{$s})){
						my @values = @{$subset{$s}};
						$subsetSignature{$mmethods{$s}}=\@values;
					}
				}

				for my $s (keys(%subsetSignature)){	
					my @values = @{$subsetSignature{$s}};

					for my $v (@values){
						my $com = $v;
						$v=~s/^\d+\s//g;
						$com=~s/\(/ /g;
						$com=~s/\)//g;
						if ($com=~/\b(TODO|FIXME|HACK|XXX)\b/){
							$v=~s/,/ /g;
							$v=~s/\s+/ /g;
							my $beginEnd = searchBeginEnd($s, \%mmethods);		
							print $commit.",".$afile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
						}else{
							$command = "java -jar ".$detectorjarPath." test -c".$com;
							$execute =`$command`;
							$v=~s/,/ /g;
							$v=~s/\s+/ /g;
							my $beginEnd = searchBeginEnd($s, \%mmethods);		
							if ($execute=~/Not SATD/){
								print $commit.",".$afile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",Not SATD\n";
							}else{
								print $commit.",".$afile.",ADDED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
							}
						}
					}
				}
			}
			
		}

		$command = "rm ".$basePath."temporary/current/\*";
		$execute = `$command`;

	}

	chdir($projectPath);

	if (!scalar @removed == 0){
		$command = "git log --pretty=%P -n 1 ".$commit;
		my $parent=`$command`;
		chomp($parent);

		$command = "git checkout ".$parent;
		$execute = `$command`;

		for my $rfile (@added){
			my $filePath=$projectPath."".$rfile;
			if (-e $filePath){
				$command = "cp ".$filePath." ".$basePath."temporary/previous/";
				$execute = `$command`;
			}
		}

		for my $rfile (@removed){
			my @fields=split("\/", $rfile);
			chomp(@fields);
			chdir ($basePath);

			my $previous = $basePath."temporary/previous/".$fields[$#fields];

			if (-e $previous){
				$command = "perl -w ".$pathexsigscript." ".$previous." ".$srcmlPath;
				$execute = `$command`;
				my @methods = split("\n",$execute);
				chomp(@methods);

				$command = "perl -w ".$pathexcommentsscript." ".$srcmlPath." ".$previous;
				$execute = `$command`;
				my @comments = split("\n",$execute);
				chomp(@comments);

				my %mapping=%{linkCommentsAndMethods(\@comments,\@methods)};
				my %subset = %{createSubsets(\%mapping, \@methods)};
				my %mmethods = %{mapping(\@methods)};

				my %subsetSignature = ();
				for my $s (keys(%subset)){
					if (exists($mmethods{$s})){
						my @values = @{$subset{$s}};
						$subsetSignature{$mmethods{$s}}=\@values;
					}
				}

				for my $s (keys(%subsetSignature)){	
					my @values = @{$subsetSignature{$s}};

					for my $v (@values){
						my $com = $v;
						$v=~s/^\d+\s//g;
						$com=~s/\(/ /g;
						$com=~s/\)//g;
						if ($com=~/\b(TODO|FIXME|HACK|XXX)\b/){
							$v=~s/,/ /g;
							$v=~s/\s+/ /g;
							my $beginEnd = searchBeginEnd($s, \%mmethods);		
							print $commit.",".$rfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
						}else{
							$command = "java -jar ".$detectorjarPath." test -c".$com;
							$execute =`$command`;
							$v=~s/,/ /g;
							$v=~s/\s+/ /g;
							my $beginEnd = searchBeginEnd($s, \%mmethods);		
							if ($execute=~/Not SATD/){
								print $commit.",".$rfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",Not SATD\n";
							}else{
								print $commit.",".$rfile.",REMOVED,\"".$s."\",".$beginEnd.",".$v.",SATD\n";
							}
						}
					}
				}
			}
		}

		$command = "rm ".$basePath."temporary/previous/\*";
		$execute = `$command`;	

	}
}

my $end = localtime();
print STDERR "Beginning: $beginning\nEnding: $end\n";