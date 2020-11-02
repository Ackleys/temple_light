import React, {Component} from 'react';

export default class extends Component<{
  children: (param: {show: () => void, hide: () => void, state: boolean}) => JSX.Element,
}, {
  visible: boolean,
}> {

  readonly state = {
    visible: false,
  }

  setVisible(visible: boolean) {
    this.setState({
       visible,
    });
  }

  render() {
    return (
      <>
        {this.props.children({
          show: () => this.setVisible(true), 
          hide: () => this.setVisible(false), 
          state: this.state.visible,
        })}
      </>
    );
  }
};