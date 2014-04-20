#tsc includes "node" call. You need this line for resolve that.
export PATH=/usr/local/bin:/usr/bin

# $1 = project path.
projectPath=$1
logPath=$projectPath/tscompile.log

# add sign for starting compiling
echo start > $logPath

# collect *.ts files
allTypeScriptPaths=$(find $projectPath -name *.ts) 


/usr/local/bin/tsc $allTypeScriptPaths 2>> $logPath

# The tsc command never tells the finish of compiling... 
# Because of that, if new line will exist in the logPath after compiling, it means compile failed with error.
# Or not, succeeded to compile.
var=`tail -1 $logPath`
if [ "$var" == "start" ]
	then
	echo typescript compile succeeded. >> $logPath
else
	echo typescript compile failure. >> $logPath
fi


