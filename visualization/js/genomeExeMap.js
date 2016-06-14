
// Setup data-specific parameters
var dataPath = "data/fake-final_dominant_genome_usages.csv";
var yDomain = [0, 4000];
var xDomain = [0, 100];
var genomeExecutionMapWidth = 15;
var envSpacer = 1;
var phenSpacer = 3;
var phenotypeIndicatorWidth = 5;
var siteHeight = 3;
var verticalMapBuffer = 50
var repCanvasBuffer = 5;
// Colors from colorbrewer
var colorsRange = ['#fff5eb', '#7f2704'];
var legendElementWidth = 5;

var currentTreatment = "cycle-200-full-restricted";
var currentReplicate = "cycle-200-full-restricted__rep_1";
var treatments = [];
var repsByTreatment = {};
var totalSitesByTreatment = {}

// Setup canvas parameters
var margin = {top: 20, right: 40, bottom: 20, left: 100};
var frameWidth = 1500;
var frameHeight = 20000;
var canvasWidth = frameWidth - margin.left - margin.right;
var canvasHeight = frameHeight - margin.top - margin.bottom;


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
    totalSitesByTreatment[treatment] = 0;
  }
  // Build reps by treatment dictionary
  if (repsByTreatment[treatment].indexOf(replicate) == -1) {
    repsByTreatment[treatment].push(replicate);
  }
  // Update total sites for this treatment.
  totalSitesByTreatment[treatment] += sites.length;
  return {
    treatment: treatment,
    replicate: replicate,
    environment: environment,
    sites: siteInfo
  };
}

dataCallback = function(data) {
  // Here is where we do some initial setup post data retrieval.
  // Setup canvas
  var chartArea = d3.select("#chart_area");

  var frame = chartArea.append("svg");
  var canvas = frame.append("g");
  frame.attr({"width": frameWidth, "height": frameHeight});
  canvas.attr({"transform": "translate(" + margin.left + "," + margin.top + ")"});


  var refreshDash = function() {
    /* This function refreshes the visualization dashboard. */
    // Populate the treatment dropdown
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
    // Update the treatment button label
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
    /* Here is where we update the page. */
    // Refresh the dashboard.
    refreshDash();
    // Get the replicates for this treatment.
    var replicates = repsByTreatment[currentTreatment];
    // Clean up canvas
    canvas.selectAll("g").remove();

    xDomain = [0, 100];
    yDomain = [0, (siteHeight * totalSitesByTreatment[currentTreatment] * 0.5) + ((repCanvasBuffer + verticalMapBuffer) * replicates.length)];
    frameHeight = (yDomain[1] * 10) * 0.5;
    frameWidth = (xDomain[1] * 10)
    canvasWidth = frameWidth - margin.left - margin.right;
    canvasHeight = frameHeight - margin.top - margin.bottom;
    // update canvas and frame
    frame.attr({"width": frameWidth, "height": frameHeight});
    canvas.attr({"transform": "translate(" + margin.left + "," + margin.top + ")"});
    /////////////////////////////
    // AXES
    /////////////////////////////
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
    ///////////////////////////////
    // DATA STUFF
    ///////////////////////////////
    // Setup data canvas
    var dataCanvas = canvas.append("g").attr({"class": "data_canvas"});
    // Clear everything from dataCanvas
    dataCanvas.selectAll("g").remove();
    dataCanvas.selectAll("line").remove();
    // Filter down to just this treatment.
    var treatmentData = data.filter(function(d) {
                                            return (d.treatment == currentTreatment);
                                          });
    // Draw each replicate genome map
    var repVerticalLocation = 0;
    for (var r = 0; r < replicates.length; r++) {
      //////////////////////////
      // Draw separator line between replicates
      //////////////////////////
      dataCanvas.append("line")
                .attr({"stroke": "black",
                       "x1": xScale(0),
                       "y1": yScale(repVerticalLocation),
                       "x2": xScale(xDomain[1]),
                       "y2": yScale(repVerticalLocation)
                     });
      console.log(replicates[r]);
      //////////////////////////
      // Organize/retrieve relevant data
      //////////////////////////
      // Filter down to just this replicate's data
      var repData = treatmentData.filter(function(d) { return d.replicate == replicates[r] });
      // Get environment-specific data for this replicate
      var envNAND = repData.filter(function(d) { return d.environment == "nand+not-"; })[0];
      var envNOT = repData.filter(function(d) { return d.environment == "nand-not+"; })[0];
      console.log(envNAND);
      console.log(envNOT);
      // Get the maximum # of executions
      var maxExecutions = d3.max([d3.max(envNAND.sites, function(d) { return d.usage; }),  d3.max(envNOT.sites, function(d) { return d.usage; }) ]);
      //////////////////////////
      // Setup color scale for heatmap
      //////////////////////////
      var colorScale = d3.scale.linear()
                          .domain([0, maxExecutions])
                          .range(colorsRange);
      //////////////////////////
      // Make replicate canvas and sub-canvases
      //////////////////////////
      // The one canvas to rule them all (for this replicate)
      console.log(repVerticalLocation);
      var repCanvas = dataCanvas.append("g").attr({
        "class": replicates[r],
        "transform": "translate(" + xScale(0) + "," + yScale(repVerticalLocation + repCanvasBuffer) + ")"
      });
      // ENV-NAND canvas
      var envNANDCanvas = repCanvas.append("g").attr({"class": "env_nand_canvas"});
      // ENV-NOT canvas
      var envNOTCanvas = repCanvas.append("g").attr({"class": "env_not_canvas"});
      //////////////////////////
      // Draw ENV-NAND
      //////////////////////////
      var nandMap = envNANDCanvas.selectAll("rect").data(envNAND.sites);
      nandMap.enter().append("rect");
      nandMap.exit().remove();
      nandMap.attr({"y": function(d, i) { return yScale(i * siteHeight); },
                    "x": function(d, i) { return xScale(0); },
                    "height": function(d, i) { return yScale(siteHeight); },
                    "width": function(d, i) { return xScale(genomeExecutionMapWidth); },
                    "class": function(d, i) { return d.inst; },
                    "fill": function(d, i) { return colorScale(Number(d.usage)); }
                    });
      //////////////////////////
      // Draw ENV-NOT
      //////////////////////////
      var notMap = envNOTCanvas.selectAll("rect").data(envNOT.sites);
      notMap.enter().append("rect");
      notMap.exit().remove();
      notMap.attr({"y": function(d, i) { return yScale(i * siteHeight); },
                   "x": function(d, i) { return xScale(genomeExecutionMapWidth + envSpacer); },
                   "height": function(d, i) { return yScale(siteHeight); },
                   "width": function(d, i) { return xScale(genomeExecutionMapWidth); },
                   "class": function(d, i) { return d.inst; },
                   "fill": function(d, i) { return colorScale(Number(d.usage)); }
                  });
      //////////////////////////
      // Draw Legend
      //////////////////////////
      var legend = repCanvas.selectAll(".legend").data(colorScale.ticks(maxExecutions).reverse());
      // Make groups with correct transform for each part of legend
      legend.enter().append("g")
                    .attr({"class": "legend",
                           "transform": function(d, i) { return "translate(" + xScale((genomeExecutionMapWidth + envSpacer) * 3) + "," + (yScale(siteHeight) + (i * yScale(siteHeight))) + ")"; }
                         });
      legend.append("rect")
            .attr({"width": xScale(genomeExecutionMapWidth / 2),
                   "height": yScale(siteHeight),
                   "fill": colorScale
                  });
      legend.append("text")
            .attr({"x": xScale(genomeExecutionMapWidth / 2 + 1),
                   "y": yScale(0.5 * siteHeight),
                   "dy": "0.25em"
                 })
            .text(String);
      //////////////////////////
      // Draw labels for this replicate
      //////////////////////////
      // replicate label
      // ENV-NAND Map label
      // ENV-NOT map label
      // legend label
      // legend site-execution labels
      // Site labels
      //////////////////////////
      // Update vertical location for next replicate
      //////////////////////////
      repVerticalLocation += (verticalMapBuffer + (envNAND.sites.length * siteHeight));
    }


    // LEGEND

    // legend.append("text")
    //       .attr({"x": xScale((genomeExecutionMapWidth / 2) + 1),
    //              "y": yScale(siteHeight - (0.5 * siteHeight)),
    //              "dy": ".35em"})
    //              .text(String);
    // dataCanvas.append("text")
    //           .attr({"class": "legend_label",
    //                  "x": xScale((genomeExecutionMapWidth + envSpacer) * 3),
    //                  "y": yScale(2)
    //                 })
    //           .text("Legend");
    //
    // // Draw environment site maps
    // // - Add new map groups

    // // - ENV-NOT
    // var notMap = envNOTCanvas.selectAll("rect").data(envNOTData.sites);
    // notMap.enter().append("rect");
    // notMap.exit().remove();
    // notMap.attr({"y": function(d, i) { return yScale(i * siteHeight); },
    //              "x": function(d, i) { return xScale(genomeExecutionMapWidth + envSpacer); },
    //              "height": function(d, i) { return yScale(siteHeight); },
    //              "width": function(d, i) { return xScale(genomeExecutionMapWidth); },
    //              "class": function(d, i) { return d.inst; },
    //              "fill": function(d, i) { return colorScale(Number(d.usage)); }
    //             });
    // // SITE LABELS
    // var siteLabelCanvas = dataCanvas.append("g");
    // var siteLabels = siteLabelCanvas.selectAll("text").data(envNANDData.sites);
    // siteLabels.enter().append("text");
    // siteLabels.exit().remove();
    // siteLabels.attr({"x": function(d, i) { return xScale((genomeExecutionMapWidth + envSpacer) * 2); },
    //                  "y": function(d, i) { return yScale((i * siteHeight) + (siteHeight / 2)); },
    //                  "dy": ".35em"
    //                })
    //           .text(function(d, i) { return "Site " + i + ": " + d.inst; });
  }
  update();

}

var main = function() {
  // Load data from csv and setup d3 callback
  d3.csv(dataPath, dataAccessor, dataCallback);
}

// Call to main
main();
