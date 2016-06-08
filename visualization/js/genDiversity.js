
// Setup data-specific parameters
var dataPath = "data/compiled_pop_stats.csv";
var xDomain = [0, 100000];
var yDomain = [0, 10];
var currentTreatment = "baseline-unrestricted";
var treatments = [];
var repsByTreatment = {};

// Setup canvas parameters
var margin = {top: 20, right: 40, bottom: 20, left: 100};
var frameWidth = 2500;
var frameHeight = 10000;
var canvasWidth = frameWidth - margin.left - margin.right;
var canvasHeight = frameHeight - margin.top - margin.bottom;

// Setup the canvas
var chartArea = d3.select("#chart_area");
var frame = chartArea.append("svg");
var canvas = frame.append("g");
frame.attr({"width": frameWidth, "height": frameHeight});
canvas.attr({"transform": "translate(" + margin.left + "," + margin.top + ")"});

// Function for translating environments form format in csv to format used by visual.
var envTranslate = function(env) {
  env_table = {"nand+not-": "ENV-NAND", "nand-not+": "ENV-NOT"};
  return env_table[env];
}

// Setup axes
//  - X Axis
var xScale = d3.scale.linear();
xScale.domain(xDomain).range([0, canvasWidth]);
var xAxis = d3.svg.axis().scale(xScale).orient("bottom");
canvas.append("g").attr({"class": "x_axis", "transform": "translate(0," + canvasHeight + ")"}).call(xAxis);
//  - Y Axis
var yScale = d3.scale.linear();
yScale.domain(yDomain).range([canvasHeight, 0]);
var yAxis = d3.svg.axis().scale(yScale).orient("left");
canvas.append("g").attr({"class": "y_axis"}).call(yAxis);

var dataAccessor = function(row) {
  var treatment = row.treatment;
  var replicate = row.replicate;
  var update = Number(row.update);
  var popSize = Number(row.population_size);
  var environment = row.environment;
  var geneticDiversity = Number(row.genotype_diversity);
  // Build treatment list
  if (treatments.indexOf(treatment) == -1) {
    // If we haven't seen this treatment yet, add it to our list of treatments.
    treatments.push(treatment);
    repsByTreatment[treatment] = [];
  }
  if (repsByTreatment[treatment].indexOf(replicate) == -1) {
    repsByTreatment[treatment].push(replicate);
  }
  return {
    treatment: treatment,
    replicate: replicate,
    update: update,
    popSize: popSize,
    environment: environment,
    geneticDiversity: geneticDiversity
  };
}

var dataCallback = function(data) {
  // Setup data canvas
  var dataCanvas = canvas.append("g").attr({"class": "data_canvas"});
  // Setup environment indicator canvas
  //var envCanvas = canvas.append("g").attr({"class": "env_canvas"});

  var refreshDash = function() {
    // Populate dashboard controls
    // - Populate treatment dropdown
    var treatmentDropDown = $("#treatment-selection-dropdown");
    treatmentDropDown.empty();
    $.each(treatments, function(i, p) {
      var li = $("<li/>")
                .appendTo(treatmentDropDown);
      var a = $("<a/>")
                .attr({"value": this, "href": "#"})
                .text(this)
                .appendTo(li);
    });
    // - Update treatment button label
    var treatDDButton = $("#treatment_selector").text(currentTreatment);
    $("<span/>").attr({"class": "caret"}).appendTo(treatDDButton);
    // Setup component listeners. (these get nuked when I nuke the dropdown with the empty function)
    $(document).ready(function() {
      // Treatment selector
      $("#treatment-selection-dropdown li a").click(function() {
        var selection = $(this).attr("value");
        // Update the current treatment
        currentTreatment = selection;
        // call for an update
        update();
      });
    });
  }

  var update = function() {
    // This is where we draw things.
    refreshDash();
    // Rep color scale
    var c10 = d3.scale.category10();
    // var color = d3.scale.linear().domain([0, len(repsByTreatment[currentTreatment])])
    //                               .range([""])
    // filter data by current treatment
    var treatmentData = data.filter(function(d) { return d.treatment == currentTreatment; });

    // line function for genetic diversity
    var lineFunction = d3.svg.line()
                               .x(function(d) { return xScale(d.update); })
                               .y(function(d) { return yScale(d.geneticDiversity); })
                               .interpolate("linear");
    // clear all rep groups
    dataCanvas.selectAll("g").remove();
    // for each replicate, filter by that replicate and draw a new line
    for (i in repsByTreatment[currentTreatment]) {
      var repCanvas = dataCanvas.append("g");
      // todo: make another canvas for this rep
      curRep = repsByTreatment[currentTreatment][i];
      repData = treatmentData.filter(function(d) { return d.replicate == curRep; })
                             .sort(function(a, b) { return a.update - b.update; });

      var repLine = repCanvas.selectAll("path").data(repData);
      repLine.enter().append("path");
      repLine.exit().remove();
      repLine.attr({
        "d": lineFunction(repData),
        "fill": "none",
        "stroke-width": 1,
        "stroke": "#a6cee3"
      });
      ////
      // Draw as a bunch of dots
      // var genDivDots = dataCanvas.selectall("circle").data(filteredData);
      // genDivDots.enter().append("circle");
      // genDivDots.exit().remove();
      // genDivDots.attr({
      //   "x": function(d) { return }
      // })
    }
  }
  update();
}

var main = function() {
  // Load data from csv and setup d3 callback
  d3.csv(dataPath, dataAccessor, dataCallback);
}

// Call our main function.
main();
