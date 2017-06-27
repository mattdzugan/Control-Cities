
var myAreas,myLines;
var myAreaGeoms = [];
var myLineGeoms = [];
//Dropdown


d3.json("./data/cityList.json", function(error, io) {
  if (error) throw error;
  $(".cityMapVizDropDown").select2({
    data: io
  });
  //var initHash = window.location.hash;
  $('.cityMapVizDropDown').select2().val([1840020491, 1840021117, 1840001651]).trigger("change");
  /*
  if (!initHash || initHash.length<5 ){
  }else{
    var noHash = initHash.substr(1);
    var listOfCityIDstrings = noHash.split('and');
    var listOfCityIDNums = listOfCityIDstrings.map(Number);
    $('.cityMapVizDropDown').select2().val(listOfCityIDNums).trigger("change");
  }*/
});
$('.cityMapVizDropDown').on('change', function (evt) {
  // Clear the things (yeah this is wasteful, i'll do the enter/exit later)
  myAreaGeoms = [];
  myLineGeoms = [];
  d3.selectAll(".cityArea").remove();
  d3.selectAll(".cityLine").remove();
  // render the things
  var cityIDs = $('.cityMapVizDropDown').select2().val()
  cityIDs.forEach(function(d,i){plotThisCity(d);});
  //var newHash = "#"+cityIDs.join('and');
  //window.location = newHash;


});


//.range(["#69b93c","#58BFAC","#4682B4","#914D90","#ED7664","#FFC445"]);
// create all the textures
var lime   = "rgba(105,185,60,1)",
    green  = "rgba(88,191,172,1)",
    blue   = "rgba(70,130,180,1)",
    purple = "rgba(145,77,144,1)",
    orange = "rgba(237,118,100,1)",
    yellow = "rgba(255,196,69,1)";
var limeT   = "rgba(105,185,60,0.05)",
    greenT  = "rgba(88,191,172,0.15)",
    blueT   = "rgba(70,130,180,0.05)",
    purpleT = "rgba(145,77,144,0.05)",
    orangeT = "rgba(237,118,100,0.05)",
    yellowT = "rgba(255,196,69,0.20)";




var tx1 = textures.lines()
  .thicker()
  .orientation("vertical")
  .strokeWidth(0.5)
  .background(limeT)
  .stroke(lime);
var tx2 = textures.lines()
  .thicker()
  .orientation("vertical")
  .strokeWidth(0.5)
  .background(greenT)
  .stroke(green);
var tx3 = textures.lines()
  .thicker()
  .orientation("vertical")
  .strokeWidth(0.5)
  .background(blueT)
  .stroke(blue);
var tx4 = textures.lines()
  .thicker()
  .orientation("vertical")
  .strokeWidth(0.5)
  .background(yellowT)
  .stroke(yellow);
var tx5 = textures.lines()
  .thicker()
  .orientation("vertical")
  .strokeWidth(0.5)
  .background(orangeT)
  .stroke(orange);
var tx6 = textures.lines()
  .thicker()
  .orientation("vertical")
  .strokeWidth(0.5)
  .background(purpleT)
  .stroke(purple);

var tx7 = textures.lines()
  .orientation("3/8", "7/8")
  .strokeWidth(0.5)
  .background(limeT)
  .stroke(lime);
var tx8 = textures.lines()
  .orientation("3/8", "7/8")
  .strokeWidth(0.5)
  .background(greenT)
  .stroke(green);
var tx9 = textures.lines()
  .orientation("3/8", "7/8")
  .strokeWidth(0.5)
  .background(blueT)
  .stroke(blue);
var tx10 = textures.lines()
  .orientation("3/8", "7/8")
  .strokeWidth(0.5)
  .background(yellowT)
  .stroke(yellow);
var tx11 = textures.lines()
  .orientation("3/8", "7/8")
  .strokeWidth(0.5)
  .background(orangeT)
  .stroke(orange);
var tx12 = textures.lines()
  .orientation("3/8", "7/8")
  .strokeWidth(0.5)
  .background(purpleT)
  .stroke(purple);

var tx13 = textures.circles()
  .lighter()
  .complement()
  .background(limeT)
  .radius(2)
  .stroke(lime)
  .fill("transparent")
  .strokeWidth(0.5);
var tx14 = textures.circles()
  .lighter()
  .complement()
  .background(greenT)
  .radius(2)
  .stroke(green)
  .fill("transparent")
  .strokeWidth(0.5);
var tx15 = textures.circles()
  .lighter()
  .complement()
  .background(blueT)
  .radius(2)
  .stroke(blue)
  .fill("transparent")
  .strokeWidth(0.5);
var tx16 = textures.circles()
  .lighter()
  .complement()
  .background(yellowT)
  .radius(2)
  .stroke(yellow)
  .fill("transparent")
  .strokeWidth(0.5);
var tx17 = textures.circles()
  .lighter()
  .complement()
  .background(orangeT)
  .radius(2)
  .stroke(orange)
  .fill("transparent")
  .strokeWidth(0.5);
var tx18 = textures.circles()
  .lighter()
  .complement()
  .background(purpleT)
  .radius(2)
  .stroke(purple)
  .fill("transparent")
  .strokeWidth(0.5);

var tx19 = textures.paths()
  .d("hexagons")
  .size(7)
  .background(limeT)
  .stroke(lime)
  .strokeWidth(0.5);
var tx20 = textures.paths()
  .d("hexagons")
  .size(7)
  .background(greenT)
  .stroke(green)
  .strokeWidth(0.5);
var tx21 = textures.paths()
  .d("hexagons")
  .size(7)
  .background(blueT)
  .stroke(blue)
  .strokeWidth(0.5);
var tx22 = textures.paths()
  .d("hexagons")
  .size(7)
  .background(yellowT)
  .stroke(yellow)
  .strokeWidth(0.5);
var tx23 = textures.paths()
  .d("hexagons")
  .size(7)
  .background(orangeT)
  .stroke(orange)
  .strokeWidth(0.5);
var tx24 = textures.paths()
  .d("hexagons")
  .size(7)
  .background(purpleT)
  .stroke(purple)
  .strokeWidth(0.5);

var tx25 = textures.paths()
  .d("nylon")
  .background(limeT)
  .stroke(lime)
  .strokeWidth(0.5);
var tx26 = textures.paths()
  .d("nylon")
  .background(greenT)
  .stroke(green)
  .strokeWidth(0.5);
var tx27 = textures.paths()
  .d("nylon")
  .background(blueT)
  .stroke(blue)
  .strokeWidth(0.5);
var tx28 = textures.paths()
  .d("nylon")
  .background(yellowT)
  .stroke(yellow)
  .strokeWidth(0.5);
var tx29 = textures.paths()
  .d("nylon")
  .background(orangeT)
  .stroke(orange)
  .strokeWidth(0.5);
var tx30 = textures.paths()
  .d("nylon")
  .background(purpleT)
  .stroke(purple)
  .strokeWidth(0.5);

var tx31 = textures.paths()
  .d("waves")
  .thicker()
  .strokeWidth(0.5)
  .background(limeT)
  .stroke(lime);
var tx32 = textures.paths()
  .d("waves")
  .thicker()
  .strokeWidth(0.5)
  .background(greenT)
  .stroke(green);
var tx33 = textures.paths()
  .d("waves")
  .thicker()
  .strokeWidth(0.5)
  .background(blueT)
  .stroke(blue);
var tx34 = textures.paths()
  .d("waves")
  .thicker()
  .strokeWidth(0.5)
  .background(yellowT)
  .stroke(yellow);
var tx35 = textures.paths()
  .d("waves")
  .thicker()
  .strokeWidth(0.5)
  .background(orangeT)
  .stroke(orange);
var tx36 = textures.paths()
  .d("waves")
  .thicker()
  .strokeWidth(0.5)
  .background(purpleT)
  .stroke(purple);

var colorList  = [lime,  green,  blue,  yellow,  orange,  purple];
var colorListT = [limeT, greenT, blueT, yellowT, orangeT, purpleT];
var textureList = [ tx1,  tx2,  tx3,  tx4,  tx5,  tx6,
                    tx7,  tx8,  tx9,  tx10, tx11, tx12,
                    tx13, tx14, tx15, tx16, tx17, tx18,
                    tx19, tx20, tx21, tx22, tx23, tx24,
                    tx25, tx26, tx27, tx28, tx29, tx30,
                    tx31, tx32, tx33, tx34, tx35, tx36];






var pi = Math.PI,
    tau = 2 * pi;

var cmwidth  = 720;
var cmheight = 400;

// Initialize the projection to fit the world in a 1×1 square centered at the origin.
var cmprojection = d3.geoMercator()
    .scale(1 / tau)
    .translate([0, 0]);

var cmpath = d3.geoPath()
    .projection(cmprojection);

var tile = d3.tile()
    .size([cmwidth, cmheight]);

var zoom = d3.zoom()
    .scaleExtent([1 << 11, 1 << 20])
    .on("zoom", zoomed);

var cmsvg = d3.select(".cityMapVizMap")
    .attr("width", cmwidth)
    .attr("height", cmheight);

cmsvg.call(tx7);  cmsvg.call(tx8);  cmsvg.call(tx9);  cmsvg.call(tx10);  cmsvg.call(tx5);  cmsvg.call(tx6);
cmsvg.call(tx1);  cmsvg.call(tx2);  cmsvg.call(tx3);  cmsvg.call(tx4);   cmsvg.call(tx11); cmsvg.call(tx12);
cmsvg.call(tx13); cmsvg.call(tx14); cmsvg.call(tx15); cmsvg.call(tx16);  cmsvg.call(tx17); cmsvg.call(tx18);
cmsvg.call(tx19); cmsvg.call(tx20); cmsvg.call(tx21); cmsvg.call(tx22);  cmsvg.call(tx23); cmsvg.call(tx24);
cmsvg.call(tx25); cmsvg.call(tx26); cmsvg.call(tx27); cmsvg.call(tx28);  cmsvg.call(tx29); cmsvg.call(tx30);
cmsvg.call(tx31); cmsvg.call(tx32); cmsvg.call(tx33); cmsvg.call(tx34);  cmsvg.call(tx35); cmsvg.call(tx36);


var raster = cmsvg.append("g");
var cmcenter = cmprojection([-98.5, 39.5]);
cmsvg
    .call(zoom)
    .call(zoom.transform, d3.zoomIdentity
        .translate(cmwidth / 2, cmheight / 2)
        .scale(1 << 12)
        .translate(-cmcenter[0], -cmcenter[1]));



function plotThisCity(cc){
  //1840021117
  d3.json(("./data/cities/"+cc+".json"), function(error, city) {
    if (error) throw error;
    myAreas = city.areas;
    myLines = city.lines;
    myAreaGeoms.push.apply(myAreaGeoms,myAreas.geometries);
    myLineGeoms.push.apply(myLineGeoms,myLines.geometries);

    // pick the texture;
    var cID = (Number(cc) % 6);
    var tID = (Number(cc) % 36);


    cmsvg.selectAll(".cityArea")
      .data(myAreaGeoms)
      .enter()
      .append("path")
        .attr("d",function(d){return cmpath(d);})
        .attr("class","cityArea")
        .style("fill", textureList[tID].url());

    cmsvg.selectAll(".cityLine")
      .data(myLineGeoms)
      .enter()
      .append("path")
        .attr("d",function(d){return cmpath(d);})
        .style("stroke",colorList[cID])
        .style("stroke-width","2px")
        .attr("class","cityLine");

  });

}








function zoomed() {
  var transform = d3.event.transform;

  var tiles = tile
      .scale(transform.k)
      .translate([transform.x, transform.y])
      ();
  //*
  cmprojection
      .scale(transform.k / tau)
      .translate([transform.x, transform.y]);

  cmsvg.selectAll(".cityArea").data(myAreaGeoms).attr("d",function(d){return cmpath(d);});
  cmsvg.selectAll(".cityLine").data(myLineGeoms).attr("d",function(d){return cmpath(d);});
  //*/
  /*
  cmsvg.selectAll(".cityArea").attr("transform",transform);
  cmsvg.selectAll(".cityLine").attr("transform",transform).style("stroke-width",1/transform.k);
  */

  var image = raster
      .attr("transform", stringify(tiles.scale, tiles.translate))
    .selectAll("image")
    .data(tiles, function(d) { return d; });

  image.exit().remove();

  image.enter().append("image")
      //.attr("xlink:href", function(d) { return "http://" + "abc"[d[1] % 3] + ".tile.openstreetmap.org/" + d[2] + "/" + d[0] + "/" + d[1] + ".png"; })
      .attr("xlink:href", function(d) { return "https://" + "cartodb-basemaps-" + "abc"[d[1] % 3] + ".global.ssl.fastly.net/light_all/" + d[2] + "/" + d[0] + "/" + d[1] + ".png"; })
      .attr("x", function(d) { return d[0] * 256; })
      .attr("y", function(d) { return d[1] * 256; })
      .attr("width", 256)
      .attr("height", 256);
}

function stringify(scale, translate) {
  var k = scale / 256, r = scale % 1 ? Number : Math.round;
  return "translate(" + r(translate[0] * scale) + "," + r(translate[1] * scale) + ") scale(" + k + ")";
}
