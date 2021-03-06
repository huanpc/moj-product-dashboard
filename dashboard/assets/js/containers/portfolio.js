import React, { Component } from 'react';
import Spinner from 'react-spinkit';

import { ProductTable } from '../components/product-table';
import { getPortfolioData } from '../libs/models';
import { values } from '../libs/utils';


/**
 * React component for portfolio
 */
export class PortfolioContainer extends Component {
  constructor(props) {
    super(props);
    this.state = {products: [], hasData: false};
  }

  componentDidMount() {
    getPortfolioData()
      .then(portfolioData => {
        // sort by service area and then name of product
        const products = portfolioData
          .map(service => values(service.products))
          .reduce((prev, curr) => prev.concat(curr), [])
          .sort((p1, p2) => p1.name.localeCompare(p2.name));
        this.setState({products: products, hasData: true});
      });
  }

  render() {
    if (! this.state.hasData) {
      return (
        <div className="spinkit">
          <Spinner
            spinnerName='three-bounce'
          />
        </div>
      );
    };
    return (
      <div>
        <div className="portfolio-header">
          <h1 className="heading-xlarge">
            MoJ Digital Portfolio
          </h1>
        </div>
        <ProductTable
          products={this.state.products}
          showService={true}
          showFilter={true}
        />
      </div>
    );
  }
}

PortfolioContainer.propTypes = {}
