/** @jsx React.DOM */
var RouteMixin = require('../mixins/route.jsx');
var Loading = require('../shared_components/loading.jsx');
var store = require('../store.js');

module.exports = React.createClass({
    mixins: [RouteMixin],
    pageTitle: function() {
        var info = this.state.info;
        if (info) {
            return info.name;
        }
        return 'Loading title...';
    },


    getInitialState: function() {
        return {
            populating: false,
            info: null
        };
    },

    componentWillReceiveProps: function(nextProps) {
        if ((!this.state.populating && !this.state.populated) ||
           this.props.loggedIn !== nextProps.loggedIn) {
            this.populateInfo();
        }
    },

    componentDidMount: function() {
        if (!this.state.populating && !this.state.populated) {
            this.populateInfo();
        }
    },

    populateInfo: function() {
        this.setState({populating: true});

        var cachedData = store.get('title_' + this.props.url);
        if (cachedData !== null) {
            this.setState({
                info: cachedData,
                populated: true,
                populating: false
            });
            return;
        }

        url = '/api/title?url=' + encodeURIComponent(this.props.url);
        url += '&chapter_limit=-1';

        var self = this;
        this.props.ajax({
            url: url,
            dataType: 'json',
            method: 'GET',
            success: function(data) {
                data.url = self.props.url;
                store.set('title_' + self.props.url, data);
                self.setState({
                    info: data,
                    populated: true
                });
            },
            complete: function() {
                self.setState({populating: false});
            }
        });
    },

    renderChapter: function(chapter) {
        var href = '/#/chapter/' + encodeURIComponent(chapter.url);
        return (
            <a href={href} key={chapter.url} className="list-group-item">
                {chapter.name}
            </a>
        );
    },

    renderReadListBtn: function() {
        var info = this.state.info;
        var readListBtn = '';
        if (info.hasOwnProperty('is_in_read_list')) {
            if (info.is_in_read_list) {
                readListBtn = (
                    <button className="btn btn-success" disabled="disabled">
                        <i className='fa fa-lg fa-check-circle'></i> In my read list
                    </button>
                );
            } else {
                readListBtn = (
                    <button className="btn btn-success" onClick={this.addToReadList}>
                        <i className='fa fa-star'></i> Add to read list
                    </button>
                );
            }
        }
        return readListBtn;
    },

    addToReadList: function() {
        var self = this;
        this.props.ajax({
            url: '/api/read-list',
            method: 'POST',
            data: JSON.stringify({
                url: self.state.info.url,
                action: 'add'
            }),
            success: function() {
                info = self.state.info;
                info.is_in_read_list = true;
                self.setState({info: info});
                store.set('title_' + self.props.url, info);
            }
        });
    },

    render: function() {
        var body;

        if (this.state.populating) {
            body = <Loading />;

        } else if (this.state.populated) {
            var info = this.state.info;
            var permalink = '/#/title/' + encodeURIComponent(info.url);

            body = (
                <div className="title-info">
                    <div className="row">

                        <div className="col-md-4">
                            <a className="thumbnail">
                                <img src={info.thumb_url} alt="thumbnail" />
                            </a>
                        </div>

                        <div className="col-md-8">
                            <h2 className="title-name">
                                {info.name} {this.renderReadListBtn()}
                            </h2>
                            <ul>
                                <li><a href={permalink}>permanent link</a></li>
                                <li><strong>more details to be implemented...</strong></li>
                            </ul>
                        </div>
                    </div>

                    <hr />
                    <div className="list-group">
                        {info.chapters.map(this.renderChapter)}
                    </div>
                </div>
            );

        } else {
            body = 'Title info not fetched. Try again.';
        }

        return (
            <div className='title-container container'>
                {body}
            </div>
        );
    }
});
