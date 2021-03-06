import moment from 'moment';
import React, { Component } from 'react';
import Griddle from 'griddle-react';

import { statusMapping } from '../libs/models';
import { numberWithCommas, codeClimateProjectURL } from '../libs/utils';

import RedImg from '../../img/red.png';
import AmberImg from '../../img/amber.png';
import GreenImg from '../../img/green.png';


/**
 * React component for a table of products
 */
export const ProductTable = ({ products, showService, showFilter }) => {

  const displayMoney = (props) => {
    const number = numberWithCommas(Number(props.data).toFixed(0));
    return (<span>£{number}</span>);
  };

  const columnMetadata = [
    {
      'columnName': 'name',
      'order': 1,
      'displayName': 'Product',
      'customComponent': (props) => {
        let url;
        if (props.rowData.type == 'ProductGroup') {
          url = `/product-groups/${props.rowData.id}`;
        } else {
          url = `/products/${props.rowData.id}`;
        };
        return (<a href={url}>{props.data}</a>);
      },
    },
    {
      'columnName': 'phase',
      'order': 3,
      'displayName': 'Phase',
      'customComponent': (props) => {
        const val = props.data === 'Not Defined' ? '' : props.data;
        return (<span>{val}</span>);
      },
      'customCompareFn': (phase) => {
        const val = {Discovery: 0, Alpha: 1, Beta: 2, Live: 3, Ended: 4}[phase];
        return typeof val === 'undefined' ? 5 : val;
      },
    },
    {
      'columnName': 'status',
      'order': 4,
      'displayName': 'Status',
      'customComponent': (props) => {
        const status = props.data.status;
        if (status in statusMapping) {
          return (
            <strong className={statusMapping[status]}>{status}</strong>
          );
        };
        return null;
      }
    },
    {
      'columnName': 'current_fte',
      'order': 5,
      'displayName': 'Current FTE',
      'customCompareFn': Number,
      'customComponent': (props) => (
        <span>
          {Number(props.data).toFixed(1)}
        </span>),
    },
    {
      'columnName': 'cost_to_date',
      'order': 6,
      'displayName': 'Cost to date',
      'customCompareFn': Number,
      'customComponent': displayMoney,
      'cssClassName': 'money-value'
    },
    {
      'columnName': 'budget',
      'order': 7,
      'displayName': 'Budget',
      'customCompareFn': Number,
      'customComponent': displayMoney,
      'cssClassName': 'money-value'
    },
    {
      'columnName': 'financial_rag',
      'order': 8,
      'displayName': 'Financial RAG',
      'customCompareFn': (label) => {
        const mappings = {RED: 3, AMBER: 2, GREEN: 1};
        return mappings[label];
      },
      'customComponent': (props) => {
        const mapping = { RED: RedImg, AMBER: AmberImg, GREEN: GreenImg };
        return (
            <img src={ mapping[props.data] } className="rag" alt={props.data} />
          )}
    },
    {
      'columnName': 'end_date',
      'order': 9,
      'displayName': 'End date',
      'customComponent': (props) => {
        const date = moment(props.data, 'YYYY-MM-DD').format('DD/MM/YYYY');
        const val = date === 'Invalid date' ? '' : date;
        return (<span>{val}</span>);
      }
    }
  ];

  if (showService) {
    columnMetadata.push({
      'columnName': 'service_area',
      'order': 2,
      'displayName': 'Service area',
      'customCompareFn': (serv) => serv.name,
      'customComponent': (props) => {
        return (<a href={`/services/${props.data.id}`}>{props.data.name}</a>);
      },
    });
  };

  return (
    <div>
      <Griddle
        results={products}
        columns={columnMetadata.map(item => item['columnName'])}
        columnMetadata={columnMetadata}
        useGriddleStyles={false}
        bodyHeight={800}
        resultsPerPage={ products.length }
        initialSort='name'
        showFilter={showFilter}
      />
      <ExportProducts />
    </div>
  );
}

ProductTable.propTypes = {
  products: React.PropTypes.array.isRequired,
  showService: React.PropTypes.bool.isRequired,
  showFilter: React.PropTypes.bool.isRequired
}

/**
 * React component for a image which hides onError
 */
export class ImageDisappearOnError extends Component {

  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  handleError() {
    this.setState({ hasError: true });
  }

  render() {
    if (this.state.hasError) {
      return null;
    };
    return <img alt={ this.props.alt } onError={() => this.handleError()} src={ this.props.src } />;
  }
}


ImageDisappearOnError.propTypes = {
  alt: React.PropTypes.string,
  src: React.PropTypes.string.isRequired
}


export const ExternalLinkExtra = ({ baseURL }) => {
  if (baseURL.includes('github.com')) {
    const codeClimateURL = codeClimateProjectURL(baseURL);
    return (
      <div className="code-climate">
        <a href={ codeClimateURL } target="_blank">
          <ImageDisappearOnError alt="Code Climate" src={ codeClimateURL + "/badges/gpa.svg" } />
        </a>
        <a href={ codeClimateURL + '/coverage' } target="_blank">
          <ImageDisappearOnError alt="Test Coverage" src={ codeClimateURL + "/badges/coverage.svg" } />
        </a>
        <a href={ codeClimateURL } target="_blank">
          <ImageDisappearOnError alt="Issue Count" src={ codeClimateURL + "/badges/issue_count.svg" } />
        </a>
      </div>
    )
  }
  return null;
}

ExternalLinkExtra.propTypes = {
  baseURL: React.PropTypes.string.isRequired
}

/**
 * Export projects component
 */
export function ExportProducts() {
  return (
    <div className="export-container">
      <h4 className="heading-medium">Download product data</h4>
      <ul>
        <li><a href="/products/export/visible/" className="export-button">Excel (visible products only)</a></li>
        <li><a href="/products/export/all/" className="export-button">Excel (all products)</a></li>
      </ul>
    </div>
  )
}
