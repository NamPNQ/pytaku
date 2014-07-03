var TitleInfo = React.createClass({
    renderChapter: function(chapter) {
        return (
            <a href={chapter.url} className="list-group-item">
                {chapter.name}
            </a>
        );
    },

    render: function() {
        var info = this.props.info;
        return (
            <div className="title-info">
                <div className="row">

                    <div className="col-md-4">
                        <a className="thumbnail">
                            <img src={info.thumb_url} alt="thumbnail" />
                        </a>
                    </div>

                    <div className="col-md-8">
                        <ul>
                            <li><strong>Tags:</strong></li>
                            <li><strong>Lorem ipsum</strong></li>
                        </ul>
                    </div>
                </div>

                <hr />
                <div className="list-group">
                    {info.chapters.map(this.renderChapter)}
                </div>
            </div>
        );
    }
});

var Title = React.createClass({
    getInitialState: function() {
        this.populateInfo();
        return {
            populating: true
        };
    },

    populateInfo: function() {
        this.setState({populating: true});
        var self = this;
        $.ajax({
            url: '/api/title?url=' + self.props.url,
            dataType: 'json',
            method: 'GET',
            success: function(data) {
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

    render: function() {
        var titleInfo;

        if (this.state.populating) {
            titleInfo = 'Fetching title info...';
        } else if (this.state.populated) {
            titleInfo = <TitleInfo info={this.state.info} />;
        } else {
            titleInfo = 'Title info not fetched. Try again.';
        }
        return (
            <div className='title-container'>
                {titleInfo}
            </div>
        );
    }
});
