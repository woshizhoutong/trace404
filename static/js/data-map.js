function loadDataMap(mapData) {
    var renderData = {};
    for (var i = 0; i < mapData.length; i++) {
      let item = mapData[i];
      let key = item.state;
      let cases = item.confirmed_case;
      let fillKey;
      if (cases > 0 && cases < 5) {
        fillKey = 'VeryLight';
      } else if (cases >= 5) {
        fillKey = 'Light'
      }

      renderData[key] = {
        "fillKey": fillKey,
        "cases": cases,
      }
    }

    const fillKeyColorMap = {
      'VeryHeavy': '#DC143C',
      'Heavy': '#FF0000',
      'Medium': '#CD5C5C',
      'Light': '#FA8072',
      'VeryLight': '#FFA07A',
      'Default': '#D3D3D3'
    };
    var map = new Datamap({
      scope: 'usa',
      element: document.getElementById('usa-map'),
      responsive: true,
      geographyConfig: {
        highlightBorderColor: '#bada55',
        highlightFillColor: function(data) {
            if (data.fillKey) {
                return fillKeyColorMap[data.fillKey];
            }
            return fillKeyColorMap['Default'];
        },
        popupTemplate: function(geography, data) {
          return '<div class="hoverinfo">' + geography.properties.name + ' Found ' +  data.cases + ' Cases'
        },
        highlightBorderWidth: 3
      },

      fills: {
        'VeryHeavy': fillKeyColorMap['VeryHeavy'],
        'Heavy': fillKeyColorMap['Heavy'],
        'Medium': fillKeyColorMap['Medium'],
        'Light': fillKeyColorMap['Light'],
        'VeryLight': fillKeyColorMap['VeryLight'],
        defaultFill: fillKeyColorMap['Default'],
      },
      data: renderData,
      done: function(datamap) {
        datamap.svg.selectAll('.datamaps-subunit').on('click', function(geography) {
            focus = geography.id;
        });
      }
    });

    map.labels();

    window.addEventListener('resize', function() {
        map.resize();
    });
}