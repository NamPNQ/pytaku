/** @jsx React.DOM */

// TODO: Some parts of this are similar to <Title> component. Refactor the
// common part out later.
var ResultTitle = React.createClass({
    render: function() {
        var item = this.props.item;
        var tagId = 'collapse' + this.props.id;
        var href = '#' + tagId;
        var titleInfo;

        if (this.state.populated) {
            titleInfo = <TitleInfo info={this.state.info}/>;
        } else {
            titleInfo = "Fetching data...";
        }

        return (
            <div className="panel panel-default">
                <div className="panel-heading clickable"
                    data-toggle="collapse" data-target={href}
                    data-parent="#accordion" onClick={this.populateInfo}>
                    <h4 className="panel-title">
                        <a>{item.name}</a>
                        <span className="badge pull-right">{item.site}</span>
                    </h4>
                </div>
                <div id={tagId} className="panel-collapse collapse">
                    <div className="panel-body">
                        {titleInfo}
                    </div>
                </div>
            </div>
        );
    },

    getInitialState: function() {
        return {populated: false};
    },

    populateInfo: function() {
        if (this.populated) return;
        this.setState({populating: true});
        var item = this.props.item;

        var self = this;
        $.ajax({
            url: '/api/title?url=' + encodeURIComponent(item.url),
            dataType: 'json',
            method: 'GET',
            success: function(data) {
                data.url=encodeURIComponent(item.url);
                self.setState({
                    info: data,
                    populated: true
                });
            },
            complete: function() {
                self.setState({populating: false});
            }
        });
    }
});

var TitleList = React.createClass({
    css: {
        maxWidth: '800px',
        margin: '10px auto'
    },

    createTitle: function(item, id) {
        // Assign unique key to make sure outdated Title components are
        // destroyed instead of reused - http://fb.me/react-warning-keys
        var key = item.url;
        return <ResultTitle item={item} id={id} key={key} />;
    },

    render: function() {
        return (
            <div className="panel-group" id="accordion" style={this.css}>
                {this.props.items.map(this.createTitle)}
            </div>
        );
    }
});

var SearchButton = React.createClass({
    css: {margin: '10px', align: 'auto'},

    className: function() {
        var common = 'fa fa-lg ';
        if (this.props.searching) {
            common += 'fa-spinner fa-spin';
        } else {
            common += 'fa-search';
        }
        return common;
    },

    text: function() {
        if (this.props.searching) return 'Searching...';
        else return 'Search';
    },

    render: function() {
        return (
            <button className="btn btn-primary" style={this.css}>
                <i className={this.className()}></i> {this.text()}
            </button>
        );
    }
});

var Search = React.createClass({
    mixins: [RouteMixin],
    pageTitle: function() {
        var query = this.props.query;
        if (query) {
            return query + ' - Manga title search';
        } else {
            return 'Search manga title';
        }
    },

    getInitialState: function() {
        var searching = false;
        if (this.props.query) {
            this.search(this.props.query);
            searching = true;
        }
        return {
            searching: searching,
            items: []
        };
    },

    componentWillReceiveProps: function(nextProps) {
        var searching = false;
        if (nextProps.query) {
            this.search(nextProps.query);
        }
    },

    handleSubmit: function(e) {
        var query = this.refs.queryInput.state.value;
        window.location.href = '/#/search/' + query;
        return false; // So that browser won't submit an old-fashioned POST
    },

    search: function(query) {
        if (!query || query.trim().length < 2 ||
            (this.state && this.state.searching)) {
            return false;
        }
        query = query.trim();

        this.setState({searching: true});
        var self = this;
        $.ajax({
            url: '/api/search?keyword=' + encodeURIComponent(query),
            dataType: 'json',
            method: 'GET',
            success: function(data) {
                self.setState({items: data});
            },
            complete: function() {
                self.setState({searching: false});
            }
        });
    },

    css: {textAlign: 'center'},

    render: function(e) {
        return (
            <div>
                <form className="form-horizontal" role="form" style={this.css}
                    onSubmit={this.handleSubmit}>

                    <input className="form-control" type="text" ref="queryInput"
                        placeholder="Enter manga title" autoFocus="autofocus" />

                    <SearchButton searching={this.state.searching} />
                </form>

                <TitleList items={this.state.items} />
            </div>);
    }
});
