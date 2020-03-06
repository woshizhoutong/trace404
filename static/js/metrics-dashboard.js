// Animate the element's value from x to y:

function animateMetricsRampUp(val, element_id) {
    $({ someValue: 0 }).animate({ someValue: val }, {
        duration: 1000,
        easing: 'swing', // can be anything
        step: function () { // called on every step
            // Update the element's text with rounded-up value:
            element_id.text(commaSeparateNumber(Math.round(this.someValue)));
        }
    });
}

function commaSeparateNumber(val) {
    while (/(\d+)(\d{3})/.test(val.toString())) {
        val = val.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    }
    return val;
}


//data format:
//[
//  {
//    "state": "AL",
//    "name": "Alabama",
//    "case": 123
//  },
//  {
//    "state": "AK",
//    "name": "Alaska",
//    "case": 999
//  }
//]
function getTotalConfirmedCases(data) {
    var count = 0;
    for (var i = 0; i < data.length; i++) {
        let item = data[i];
        count = count + Number(item.case);
    }
    return count;
}

