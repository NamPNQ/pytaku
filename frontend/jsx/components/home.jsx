/** @jsx React.DOM */
var Home = React.createClass({
    mixins: [RouteMixin, AuthMixin],
    render: function() {
        return (
            <div className="container">
                <h2>Welcome to Pytaku!</h2>
            </div>
        );
    }
});
