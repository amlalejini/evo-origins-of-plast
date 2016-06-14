
// Setup data-specific parameters
var dataPath = "data/fake-final_dominant_genome_usages.csv";
var yDomain = [0, 200];
var xDomain = [0, 100];
var genomeExecutionMapWidth = 15;
var envSpacer = 1;
var phenSpacer = 3;
var phenotypeIndicatorWidth = 5;
var siteHeight = 3;
// Colors from colorbrewer
var colorsRange = ['#fff5eb', '#7f2704'];
var legendElementWidth = 5;

var currentTreatment = "cycle-200-full-restricted";
var currentReplicate = "cycle-200-full-restricted__rep_1";
var treatments = [];
var repsByTreatment = {};

// Setup canvas parameters
var margin = {top: 20, right: 40, bottom: 20, left: 100};
var frameWidth = 1500;
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
var xAxis = d3.svg.axis().scale(xScale).orient("top");
canvas.append("g").attr({"class": "x_axis", "fill": "none"}).call(xAxis);
// - Y axis
var yScale = d3.scale.linear();
yScale.domain(yDomain).range([0, canvasHeight]);
var yAxis = d3.svg.axis().scale(yScale).orient("left");
canvas.append("g").attr({"class": "y_axis", "fill": "none"}).call(yAxis);

var dataAccessor = function(row) {
  var treatment = row.treatment;
  var replicate = row.replicate;
  var environment = row.environment;
  var sites = row.sites.split("|");
  var siteUsage = row.site_usage.split("|");
  var normSiteUsage = row.norm_site_usage.split("|");
  // Combine sites and site usage to make things easier later
  siteInfo = [];
  for (var i = 0; i < sites.length; i++) {
    siteInfo.push({inst: sites[i], usage: siteUsage[i], normUsage: normSiteUsage[i]});
  }
  // Build treatments list
  if (treatments.indexOf(treatment) == -1) {
    treatments.push(treatment);
    repsByTreatment[treatment] = [];
  }
  // Build reps by treatment dictionary
  if (repsByTreatment[treatment].indexOf(replicate) == -1) {
    repsByTreatment[treatment].push(replicate);
  }
  return {
    treatment: treatment,
    replicate: replicate,
    environment: environment,
    sites: siteInfo
  };
}

dataCallback = function(data) {
  // Here is where we do some initial setup post data retrieval.
  // Setup data canvas
  var dataCanvas = canvas.append("g").attr({"class": "data_canvas"});

  var update = function() {
    // Here is where we draw things.
    // Clear all map groups
    dataCanvas.selectAll("g").remove();
    // Filter out data (we want to have data for ENV-NAND and ENV-NOT) for current treatment/replicate
    var filteredData = data.filter(function(d) {
                                            return (d.treatment == currentTreatment) && (d.replicate == currentReplicate);
                                          });
    var envNANDData = filteredData.filter(function(d) {
                                            return d.environment == "nand+not-";
                                          })[0];
    var envNOTData = filteredData.filter(function(d) {
                                            return d.environment == "nand-not+";
                                          })[0];
    // Create color scale
    // console.log(d3.max([d3.max(envNANDData.sites, function(d) { return d.usage; }),  d3.max(envNOTData.sites, function(d) { return d.usage; }) ]));
    // console.log([d3.max(envNANDData.sites, function(d) { return Number(d.usage); }),  d3.max(envNOTData.sites, function(d) { return Number(d.usage); })]);
    var maxExecutions = d3.max([d3.max(envNANDData.sites, function(d) { return d.usage; }),  d3.max(envNOTData.sites, function(d) { return d.usage; }) ]);
    var colorScale = d3.scale.linear()
                        .domain([0, maxExecutions])
                        .range(colorsRange);

    // LEGEND
    var legend = dataCanvas.selectAll(".legend")
                            .data(colorScale.ticks(maxExecutions).reverse())
                            .enter().append("g")
                            .attr({"class": "legend",
                                   "transform": function(d, i) { return "translate(" + xScale((genomeExecutionMapWidth + envSpacer) * 3) + "," + (yScale(siteHeight) + (i * yScale(siteHeight))) + ")"; }
                                 });
    legend.append("rect")
          .attr({"width": xScale(genomeExecutionMapWidth / 2),
                 "height": yScale(siteHeight),
                 "fill": colorScale
               });
    legend.append("text")
          .attr({"x": xScale((genomeExecutionMapWidth / 2) + 1),
                 "y": yScale(siteHeight - (0.5 * siteHeight)),
                 "dy": ".35em"})
                 .text(String);
    dataCanvas.append("text")
              .attr({"class": "legend_label",
                     "x": xScale((genomeExecutionMapWidth + envSpacer) * 3),
                     "y": yScale(2)
                    })
              .text("Legend");

    // Draw environment site maps
    // - Add new map groups
    var envNANDCanvas = dataCanvas.append("g").attr({"class": "env_nand_canvas"});
    var envNOTCanvas = dataCanvas.append("g").attr({"class": "env_not_canvas"});
    // - ENV-NAND
    var nandMap = envNANDCanvas.selectAll("rect").data(envNANDData.sites);
    nandMap.enter().append("rect");
    nandMap.exit().remove();
    nandMap.attr({"y": function(d, i) { return yScale(i * siteHeight); },
                  "x": function(d, i) { return xScale(0); },
                  "height": function(d, i) { return yScale(siteHeight); },
                  "width": function(d, i) { return xScale(genomeExecutionMapWidth); },
                  "class": function(d, i) { return d.inst; },
                  "fill": function(d, i) { return colorScale(Number(d.usage)); }
                  });
    // - ENV-NOT
    var notMap = envNOTCanvas.selectAll("rect").data(envNOTData.sites);
    notMap.enter().append("rect");
    notMap.exit().remove();
    notMap.attr({"y": function(d, i) { return yScale(i * siteHeight); },
                 "x": function(d, i) { return xScale(genomeExecutionMapWidth + envSpacer); },
                 "height": function(d, i) { return yScale(siteHeight); },
                 "width": function(d, i) { return xScale(genomeExecutionMapWidth); },
                 "class": function(d, i) { return d.inst; },
                 "fill": function(d, i) { return colorScale(Number(d.usage)); }
                });
    // SITE LABELS
    var siteLabelCanvas = dataCanvas.append("g");
    var siteLabels = siteLabelCanvas.selectAll("text").data(envNANDData.sites);
    siteLabels.enter().append("text");
    siteLabels.exit().remove();
    siteLabels.attr({"x": function(d, i) { return xScale((genomeExecutionMapWidth + envSpacer) * 2); },
                     "y": function(d, i) { return yScale((i * siteHeight) + (siteHeight / 2)); },
                     "dy": ".35em"
                   })
              .text(function(d, i) { return "Site " + i + ": " + d.inst; });
  }
  update();

}

var main = function() {
  // Load data from csv and setup d3 callback
  d3.csv(dataPath, dataAccessor, dataCallback);
}

// Call to main
main();
