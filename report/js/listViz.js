var rnk_options = {
  valueNames: [ 'rnkName', 'rnkState', 'rnkMiles', 'rnkArea', 'rnkDist', 'rnkCount', 'rnkPop', 'rnkPopTxt', { data: ['rnkId'] } ],
  page: 10,
  pagination: { name: "pagination",
                paginationClass: "pagination",
                outerWindow: 2},
  item: '<li data-rnkId><p class="rnkHead"><span class="rnkName"></span><span class="zhidden-xs">, <span class="rnkState"></span></span><span class="rnkPopLabel">Population </span><span class="rnkPopTxt"></span></p><div class="infoContainer container"><div class="col col-md-3 col-sm-3 col-xs-6"><p class="rnkInfo"><span class="rnkMiles"></span> miles of signage</p></div><div class="col col-md-3 col-sm-3 col-xs-6"><p class="rnkInfo"><span class="rnkArea"></span> miles<sup>2</sup> of territory</p></div><div class="col col-md-3 col-sm-3 col-xs-6"><p class="rnkInfo">signs on <span class="rnkCount"></span> interstates</p></div><div class="col col-md-3 col-sm-3 col-xs-6"><p class="rnkInfo"><span class="rnkDist"></span> miles to farthest sign</p></div></div></li>'
};


d3.json("./data/sortableList.json", function(error, sortableList) {
  // initalize
  var rnk_List = new List('rankings', rnk_options, sortableList.list);

  // sort by Mileage
  rnk_List.sort('rnkMiles', {order: "desc"});
  d3.selectAll("#rnkMiles").each(function(){
    d3.select(this).classed("active",true);
  });

  //apply coloring
  applyColoring(sortableList.winners);

  // Re-Sort on click
  d3.selectAll(".btnsort").on("click",function(){
    // remove any actives
    d3.selectAll(".btnsort").each(function(){
      var me = d3.select(this);
      me.classed("active",false);
    });

    // sort & activate
    var me = d3.select(this);
    var value = me.attr("id");
    rnk_List.sort(value, {order: "desc"});
    me.classed("active",true);

    //var w = sortableList.winners;
    applyColoring(sortableList.winners);

  });

});



function applyColoring(w){
  // forloops & jq below
  // :-( :-( :-( :-( :-(
  //not sure of a D3-omatic way to do this

  // highlight top 5 densities
  for (var ii=1; ii<5; ii++){
    $('li[data-rnkId='+w.t5MD[ii]+'] .rnkMiles').css("border-bottom","2px solid #2d92be");
    $('li[data-rnkId='+w.t5AD[ii]+'] .rnkArea' ).css("border-bottom","2px solid #2d92be");
    $('li[data-rnkId='+w.t5CD[ii]+'] .rnkCount').css("border-bottom","2px solid #2d92be");
    $('li[data-rnkId='+w.t5DD[ii]+'] .rnkDist' ).css("border-bottom","2px solid #2d92be");
  }
  // highlight top 5
  for (var ii=1; ii<5; ii++){
    $('li[data-rnkId='+w.t5M[ii]+'] .rnkMiles').css("border-bottom","2px solid #64b93c");
    $('li[data-rnkId='+w.t5A[ii]+'] .rnkArea' ).css("border-bottom","2px solid #64b93c");
    $('li[data-rnkId='+w.t5C[ii]+'] .rnkCount').css("border-bottom","2px solid #64b93c");
    $('li[data-rnkId='+w.t5D[ii]+'] .rnkDist' ).css("border-bottom","2px solid #64b93c");
  }
  // highlight winners densities
  $('li[data-rnkId='+w.t5MD[0]+'] .rnkMiles').css("border-bottom","5px solid #2d92be");
  $('li[data-rnkId='+w.t5AD[0]+'] .rnkArea' ).css("border-bottom","5px solid #2d92be");
  $('li[data-rnkId='+w.t5CD[0]+'] .rnkCount').css("border-bottom","5px solid #2d92be");
  $('li[data-rnkId='+w.t5DD[0]+'] .rnkDist' ).css("border-bottom","5px solid #2d92be");
  // highlight winners
  $('li[data-rnkId='+w.t5M[0]+'] .rnkMiles').css("border-bottom","5px solid #64b93c");
  $('li[data-rnkId='+w.t5A[0]+'] .rnkArea' ).css("border-bottom","5px solid #64b93c");
  $('li[data-rnkId='+w.t5C[0]+'] .rnkCount').css("border-bottom","5px solid #64b93c");
  $('li[data-rnkId='+w.t5D[0]+'] .rnkDist' ).css("border-bottom","5px solid #64b93c");

}
