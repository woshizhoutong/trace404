function loadDataMap(mapData) {
    var renderData = {};
    for (var i = 0; i < mapData.length; i++) {
      let item = mapData[i];
      let key = item.state;
      let cases = item.confirmed_case;
      let fillKey;
      if (cases == 0) {
        fillkey = 'Default';
      } else if (cases > 0 && cases < 5) {
        fillKey = 'VeryLight';
      } else if (cases >= 5 && cases <20) {
        fillKey = 'Light';
      } else if (cases >= 20 && cases <100) {
        fillKey = 'Medium';
      } else {
        fillKey = 'Heavy';
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

            $.ajax({
                url: '/api/news?state=' + geography.properties.name,
                type: 'GET',
                method: 'GET',
                dataType: 'json',
            }).done((res, textStatus, jqXHR) => {
                $('#news_container').empty();
                $('#news_location').text(geography.properties.name)
                for (var i = 0; i < res.length; i++) {
                  let title = res[i].title;
                  let url = res[i].url;
                  let img_url = res[i].img_url;
                  let description = res[i].description;
                  let publishedAt = res[i].publishedAt;
                  let source = res[i].source;

                  let news_link = `/news_page?id=${url}`;
                  const news_element =
                  `<div class="col-lg-4 mb-4" >
                    <div class="entry2">
                        <a href="${news_link}"><img src="${img_url}" onerror="this.src='https://cdn.browshot.com/static/images/not-found.png';" alt="Image" class="img-fluid rounded"></a>
                        <div class="excerpt">
                          <span class="post-category text-white bg-secondary mb-3">Politics</span>
                          <h2><a href="${news_link}">${title}</a></h2>
                          <div class="post-meta align-items-center text-left clearfix">
                            <figure class="author-figure mb-0 mr-3 float-left">From ${source}</figure>
                            <span>-&nbsp; At ${publishedAt}</span>
                          </div>
                        </div>
                        <p>${description}</p>
                      </div>
                    </div>
                  `;
                  $('#news_container').append(news_element);
                }
            }).fail((jqXHR, textStatus, errorThrown) => {
                console.log(errorThrown);
            });

        });
      }
    });

    map.labels();

    window.addEventListener('resize', function() {
        map.resize();
    });
}