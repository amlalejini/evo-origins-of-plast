
// Setup data-specific parameters
var dataPath = "data/fake_pop_stats.csv";
var validStates = ["0000","0001","0010","0011","0100","0101","0110","0111","1000","1001","1010","1011","1100","1101","1110","1111"]
var xDomain = [0, 1000];
var yDomain = [0, 3600];
var stepSize = 99
var currentTreatment = "io-sense-only";
var currentReplicate = "single_runs_1";

// Setup canvas parameters
var margin = {top: 20, right: 40, bottom: 20, left: 100};
var frameWidth = 940;
var frameHeight = 1500;
var canvasWidth = frameWidth - margin.left - margin.right;
var canvasHeight = frameHeight - margin.top - margin.bottom;

// Setup canvas
var chartArea = d3.select("#chart_area");
var frame = chartArea.append("svg");
var canvas = frame.append("g");
frame.attr({"width": frameWidth, "height": frameHeight});
canvas.attr({"transform": "translate(" + margin.left + "," + margin.top + ")"});

// Setup axes
// - X axis
var xScale = d3.scale.linear();
xScale.domain(xDomain).range([0, canvasWidth]);
var xAxis = d3.svg.axis().scale(xScale).orient("bottom");
canvas.append("g").attr({"class": "x_axis", "transform": "translate(0," + canvasHeight + ")"}).call(xAxis);
// - Y axis
var yScale = d3.scale.linear();
yScale.domain(yDomain).range([canvasHeight, 0]);
var yAxis = d3.svg.axis().scale(yScale).orient("left");
canvas.append("g").attr({"class": "y_axis"}).call(yAxis);

var dataAccessor = function(row) {
  var treatment = row.treatment;
  var replicate = row.replicate;
  var update = Number(row.update);
  var popSize = Number(row.population_size);
  var popComposition = [];
  var cummulativeVal = 0;
  for (var i = 0; i < validStates.length; i++) {
    popComposition.push({phenotype: validStates[i],
                         count: Number(row[validStates[i]]),
                         relativePos: cummulativeVal
                       });
    cummulativeVal += Number(row[validStates[i]]);
  }
  return {
    treatment: treatment,
    replicate: replicate,
    update: update,
    popSize: popSize,
    popComposition: popComposition
  };
}

var dataCallback = function(data) {
  // Setup data canvas
  var dataCanvas = canvas.append("g").attr({"class": "data_canvas"});
  // Setup environment indicator canvas
  var envCanvas = canvas.append("g").attr({"class": "env_canvas"});
  // Filter data by current treatment and replicate
  var filteredData = data.filter(function(d) {
                                    return ((d.treatment == currentTreatment) && (d.replicate == currentReplicate));
                                });

  var update = function() {
    // This is where we draw things.
    var populations = dataCanvas.selectAll("g").data(filteredData, function(d) { return String(d.update); } );
    populations.enter().append("g");
    populations.exit().remove();
    populations.attr({"id": function(d) { return String(d.update); } });
    populations.each(function(popD, i) {
      var stateBlocks = d3.select(this).selectAll("rect").data(popD.popComposition);
      stateBlocks.enter().append("rect");
      stateBlocks.exit().remove();
      // for each phenotype in this population
      stateBlocks.attr({
        "y": function(d) { return yScale(d.relativePos + d.count); },
        "x": function(d) { return xScale(popD.update); },
        "height": function(d) { return canvasHeight - yScale(d.count); },
        "width": function(d) { return xScale(stepSize); },
        "class": function(d) { return "P" + d.phenotype; }
      });
    });
  }
  update();
}

var main = function() {
  // Load data from csv and setup d3 callback
  d3.csv(dataPath, dataAccessor, dataCallback);
}

// Call our main function
main();
