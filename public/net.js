// functions
function showLoader() {
  indicator = chart.tooltipContainer.createChild(am4core.Container);
  indicator.background.fill = am4core.color("#fff");
  indicator.background.fillOpacity = 0.8;
  indicator.width = am4core.percent(100);
  indicator.height = am4core.percent(100);
  var indicatorLabel = indicator.createChild(am4core.Label);
  indicatorLabel.text = "🕸️ loading the net 🕸️";
  indicatorLabel.align = "center";
  indicatorLabel.valign = "middle";
  indicatorLabel.fontSize = 30;
}

function hideLoader() {
    indicator.hide();
}

function reset() {
    networkSeries.links.template.strength = 1;
    networkSeries.manyBodyStrength = -5;
    networkSeries.centerStrength = 0.9;
    networkSeries.data = originalData
}

function scrollToCenter() {
    window.scrollTo(screen.height / 2, screen.width / 2)
}

function setDefaultNodeStrength() {
    networkSeries.manyBodyStrength = -5;
    networkSeries.centerStrength = 0.1;
}

function filter(name) {
    var fileredData = []
    originalData.forEach(function(item) {
        if (item.linkWith.includes(name) || item.name == name) {
            fileredData.push(item)
        }
    })
    scrollToCenter()
    networkSeries.links.template.strength = 1;
    networkSeries.manyBodyStrength = -5;
    networkSeries.centerStrength = 0.1;
    networkSeries.data = fileredData

    // reset search bar
    document.getElementById("artist").reset();
    var ul = document.getElementById("artist-list");
    ul.innerHTML = ""
}

function search(value) {
    var songUl = document.getElementById("song-list");
    songUl.innerHTML = ``
    var artistUl = document.getElementById("artist-list");
    artistUl.innerHTML = ``
    const valueLen = value.length
    if (valueLen > 1) {
        var results = []
        for (var artist of artists) {
            if (artist.substring(0, valueLen) == value) {
                results.push(artist)
            }
            if (results.length == 3) {
                break
            }
        }
        results.forEach(function(result) {
            var listItem = document.createElement("li");
            listItem.innerHTML = `<button class="small-button" style="margin-bottom: 5px" onclick="filter('${result}')">${result}</button>`
            artistUl.appendChild(listItem);
        })
    }
}

function toggleChart() {
    var button = document.getElementById("toggle-chart");
    showCharts = !showCharts
    if (showCharts) {
        button.innerText = 'hide charts'
    } else {
        button.innerText = 'show charts'
        var ul = document.getElementById("song-list");
        ul.innerHTML = ``
    }
}

// chart initialize
am4core.useTheme(am4themes_animated);
var chart = am4core.create("chartdiv", am4plugins_forceDirected.ForceDirectedTree);
chart.preloader.disabled = true;

var networkSeries = chart.series.push(new am4plugins_forceDirected.ForceDirectedSeries())
networkSeries.dataSource.requestOptions.requestHeaders = [{
    "key": "Access-Control-Allow-Origin",
    "value": "*"
  },{
    "key": "Content-Type",
    "value": "application/octet-stream"
  }];
networkSeries.dataSource.url = 'https://storage.googleapis.com/collab-net-charts/net.json'

// initialize
var originalData = null
var showCharts = true
var artists = new Set()

// chart config
networkSeries.fontSize = 12;
networkSeries.linkWithStrength = 0;
networkSeries.maxRadius = 60
networkSeries.minRadius = 20
networkSeries.manyBodyStrength = -5;
networkSeries.centerStrength = 0.9;

networkSeries.dataFields.linkWith = "linkWith";
networkSeries.dataFields.name = "name";
networkSeries.dataFields.id = "name";
networkSeries.dataFields.value = "value";
networkSeries.dataFields.children = "children";
networkSeries.dataFields.songs = "songs"

// networkSeries.links.template.tooltipText = ""
var nodeTemplate = networkSeries.nodes.template;
nodeTemplate.fillOpacity = 1;
nodeTemplate.outerCircle.fill = '#999999'
nodeTemplate.label.hideOversized = false;
nodeTemplate.label.truncate = false;
nodeTemplate.label.text = "{name}"
nodeTemplate.label.fill = "#000000"

var linkTemplate = networkSeries.links.template;
linkTemplate.strokeWidth = 1;
linkTemplate.strength = 1;
var linkHoverState = linkTemplate.states.create("hover");
linkHoverState.properties.strokeOpacity = 1;
linkHoverState.properties.strokeWidth = 2;

var indicator;
showLoader();

// charts events
nodeTemplate.events.on("over", function(event) {  // hoover over
    var dataItem = event.target.dataItem;
    dataItem.childLinks.each(function(link) {
        link.isHover = true;
    })
    if (showCharts) {
        // show toggle button
        var button = document.getElementById("toggle-chart");
        button.style.visibility = 'visible'

        // add to chart list
        var ul = document.getElementById("song-list");
        ul.innerHTML = ``
        dataItem.songs.forEach(function(song, index) {
            var listItem = document.createElement("li");
            if (index % 2) {
                listItem.innerHTML = `<p class="even-row">${song}</p>`
            } else {
                listItem.innerHTML = `<p class="odd-row">${song}</p>`
            }
            ul.appendChild(listItem);
        })
    }
})

nodeTemplate.events.on("out", function(event) {  // hoover away
    var dataItem = event.target.dataItem;
    dataItem.childLinks.each(function(link) {
      link.isHover = false;
    })
})

networkSeries.nodes.template.events.on("hit", function(ev) {  // click on
    var targetNode = ev.target;
    if (targetNode.dataItem.level == 0) {
        filter(targetNode.dataItem.name)
    }
});

networkSeries.events.on("dataitemsvalidated", function(ev) {  // data loaded
    if (originalData == null && networkSeries.data.length != 0) {
        scrollToCenter()
        originalData = networkSeries.data
        originalData.forEach(function(item) {
            artists.add(item.name)
        })
    }
    console.log(networkSeries.data)
}, this);

chart.events.on("ready", function(ev){
    hideLoader();
});