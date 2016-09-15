define(function(require, exports, module) {

    var _sparkline = require("libs/jquery.sparkline");


    /**
     * Based solely on the totally insane assumption that we have three banks
     * and that the first is the sum of the two following.
     */
    function PduController($navlet, dataUrl) {
        this.$navlet = $navlet;
        this.feedBack = this.$navlet.find('.alert-box.alert');
        this.timestamp = this.$navlet.find('.alert-update-timestamp span');
        this.dataUrl = dataUrl;
        this.thresholds = getThresholds(this.$navlet.find('.pdu-load-status').data('load-thresholds'));
        this.config = getConfig(this.thresholds.length);

        this.update();
        $navlet.on('refresh', this.update.bind(this));  // navlet controller determines when to update
        $navlet.on('render', function(event, renderType){
            /* We need to unregister eventlistener, as it will not be removed
             when going into edit-mode, and thus we will have one for each time
             you have edited the widget. */
            if (renderType === 'EDIT') {
                $navlet.off('refresh');
            }
        });
    }

    PduController.prototype.update = function() {
        this.feedBack.hide();
        var self = this;

        var request = $.get(this.dataUrl, function(response) {
            _.each(response, function(data) {
                var $el = self.$navlet.find('[data-metric="' + data.target + '"]');

                var point = _.find(data.datapoints.reverse(), function(datapoint) {
                    return datapoint[0] !== null;
                });

                if (!point) {
                    $el.html('<small>No data</small>');
                    return;
                }
                var load = point[0];

                // Recalculate thresholds for the total column
                var thresholds = strEndsWith(data.target, '1')
                        ? self.thresholds.map(function(t) { return t*2; }) : self.thresholds;

                $el.sparkline([null, load].concat(thresholds), self.config);
            });
            self.timestamp.text(new Date().toLocaleString());
        });
        request.fail(function() {
            self.feedBack.html('Error fetching data').show();
        });
    };


    function getConfig(numThresholds) {
        //                  green      yellow     red
        var rangeColors = ['#A5D6A7', '#FFEE58', '#EF9A9A'];
        // The splice is necessary because of the way sparklines.js applies the colors.
        rangeColors = rangeColors.splice(0, numThresholds);

        return {
            type: 'bullet',
            performanceColor: '#333333',
            rangeColors: rangeColors.reverse(),
            tooltipFormatter: function(data) {
                if (strEndsWith(data.$el.data('metric'), 1)) {
                    return "Total load " + data.values[1] + " (max: " + data.max + ")";
                } else {
                    return "Load " + data.values[1] + " (max: " + data.max + ")";
                }
            }
        };
    }


    function strEndsWith(str, suffix) {
        return str.match(suffix+"$")==suffix;
    }

    /**
     * @param {string} threshold - comma separated string with numeric thresholds
     */
    function getThresholds(threshold) {
        if (typeof threshold === 'number') {
            return [threshold];  // single threshold
        }
        return threshold.length === 0 ? [] :
            threshold.split(',').map(function(t) {return +t;});
    }

    module.exports = PduController;

});
