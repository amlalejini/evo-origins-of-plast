
// Setup data-specific parameters
var dataPath = "data/pop_stats.csv";
var validStates = ["0000","0001","0010","0011","0100","0101","0110","0111","1000","1001","1010","1011","1100","1101","1110","1111"]
var yDomain = [0, 100000];
var xDomain = [0, 3600];
var stepSize = 499
var currentTreatment = "io-sense-only";
var currentReplicate = "single_runs_1";
var treatments = [];
var repsByTreatment = {};

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

// Function for translating environments from csv format to vis format
var envTranslate = function(env) {
  env_table = {"nand+not-": "ENV-NAND", "nand-not+": "ENV-NOT"};
  return env_table[env];

}

// Setup axes
// - X axis
var xScale = d3.scale.linear();
xScale.domain(xDomain).range([0, canvasWidth]);
var xAxis = d3.svg.axis().scale(xScale).orient("top");
canvas.append("g").attr({"class": "x_axis"}).call(xAxis);
// - Y axis
var yScale = d3.scale.linear();
yScale.domain(yDomain).range([0, canvasHeight]);
var yAxis = d3.svg.axis().scale(yScale).orient("left");
canvas.append("g").attr({"class": "y_axis"}).call(yAxis);

var dataAccessor = function(row) {
  var treatment = row.treatment;
  var replicate = row.replicate;
  var update = Number(row.update);
  var popSize = Number(row.population_size);
  var environment = row.environment;
  // Build treatment list
  if (treatments.indexOf(treatment) == -1) {
    // If we haven't seen this treatment yet, add it to list of treatments
    treatments.push(treatment);
    // Also, we should add this treatment to the reps by treatment
    repsByTreatment[treatment] = [];
  }
  // Build reps by treatment dictionary
  if (repsByTreatment[treatment].indexOf(replicate) == -1) {
    repsByTreatment[treatment].push(replicate);
  }
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
    environment: environment,
    popComposition: popComposition
  };
}

var dataCallback = function(data) {
  // Setup data canvas
  var dataCanvas = canvas.append("g").attr({"class": "data_canvas"});
  // Setup environment indicator canvas
  var envCanvas = canvas.append("g").attr({"class": "env_canvas"});

  var refreshDash = function() {
    // DEPENDS ON CURRENT TREATMENT AND CURRENT REPLICATE BEING SET
    // Populate dashboard controls
    $("#treatment-selection-dropdown").empty();
    $("#replicate-selection-dropdown").empty();
    var treatmentDropDown = $("#treatment-selection-dropdown");
    var repDropDown = $("#replicate-selection-dropdown");
    //  - Setup treatment dropdown
    $.each(treatments, function(i, p) {
      var li = $("<li/>")
                .appendTo(treatmentDropDown);
      var a = $("<a/>")
                .attr({"value": this, "href":"#"})
                .text(this)
                .appendTo(li);
    });
    //  - Setup replicate dropdown
    $.each(repsByTreatment[currentTreatment], function(i, p) {
      var li = $("<li/>")
                .appendTo(repDropDown);
      var a = $("<a/>")
                .attr({"value": this, "href": "#"})
                .text(this)
                .appendTo(li);
    });
    //  - Update button labels
    var treatDDButton = $("#treatment_selector").text(currentTreatment);
    $("<span/>").attr({"class": "caret"}).appendTo(treatDDButton);
    var repDDButton = $("#replicate_selector").text(currentReplicate);
    $("<span/>").attr({"class": "caret"}).appendTo(repDDButton);

    // Setup component listeners
    $(document).ready(function() {
      // Treatment selector
      $("#treatment-selection-dropdown li a").click(function() {
        var selection = $(this).attr("value");
        // if we change treatments, we need to reset the current replicate
        if (selection != currentTreatment) {
            currentReplicate = repsByTreatment[selection][0];
        }
        // update current treatment
        currentTreatment = selection;
        // call for an update
        update();
      });
      // Replicate selector
      $("#replicate-selection-dropdown li a").click(function() {
        var selection = $(this).attr("value");
        currentReplicate = selection;
        // call for an update
        update();
      });
    });
  }

  var update = function() {
    // This is where we draw things.
    refreshDash();
    // Filter data by current treatment and replicate
    var filteredData = data.filter(function(d) {
                                      return ((d.treatment == currentTreatment) && (d.replicate == currentReplicate));
                                  });
    // Draw environment
    var environments = envCanvas.selectAll("rect").data(filteredData);
    environments.enter().append("rect");
    environments.exit().remove();
    environments.attr({
      "x": function(d) { return xScale(3650); },
      "y": function(d) { return yScale(d.update); },
      "width": function(d) { return 5; },
      "height": function(d) { return yScale(stepSize); },
      "class": function(d) { return envTranslate(d.environment); }
    });
    // Draw population stats
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
        "x": function(d) { return xScale(d.relativePos); },
        "y": function(d) { return yScale(popD.update); },
        "width": function(d) { return xScale(d.count); },
        "height": function(d) { return yScale(stepSize); },
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
