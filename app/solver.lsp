/********** solver.lsp **********/

function input() {
    usage = "\nUsage: localsolver solver.lsp "
        + "inFileName=inputFile [solFileName=outputFile] [lsTimeLimit=timeLimit]\n";

    if (inFileName == nil) error(usage);

    inFile = openRead(inFileName);
    nbItems = readInt(inFile);
    weights[i in 0..nbItems-1] = readInt(inFile);
    prices[i in 0..nbItems-1] = readInt(inFile);
    knapsackBound = readInt(inFile);
}

function model() {
    // 0-1 decisions
    x[i in 0..nbItems-1] <- bool();

    // weight constraint
    knapsackWeight <- sum[i in 0..nbItems-1](weights[i] * x[i]);
    constraint knapsackWeight <= knapsackBound;

    // maximize value
    knapsackValue <- sum[i in 0..nbItems-1](prices[i] * x[i]);
    maximize knapsackValue;
}

function param() {
    if (lsTimeLimit == nil) lsTimeLimit = 10;
    if (lsNbThreads == nil) lsNbThreads = 1;
}

function output() {
    if(solFileName == nil) return;
    println("Write solution into file '" + solFileName + "'");
    solFile = openWrite(solFileName);
    for [i in 0..nbItems-1 : getValue(x[i]) == 1]
        println(solFile, i);
}
