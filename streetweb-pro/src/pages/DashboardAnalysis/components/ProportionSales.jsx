import { Card, Radio } from 'antd';
import { FormattedMessage } from 'umi';
import React from 'react';
import { Pie } from './Charts';
import Yuan from '../utils/Yuan';
import styles from '../style.less';

const ProportionSales = ({
  dropdownGroup,
  salesType,
  loading,
  salesPieData,
  handleChangeSalesType,
}) => (
  <Card
    loading={loading}
    className={styles.salesCard}
    bordered={false}
    title={
      <FormattedMessage
        id="dashboardanalysis.analysis.the-proportion-of-sales"
        defaultMessage="The Proportion of Sales"
      />
    }
    style={{
      height: '100%',
    }}
    extra={
      <div className={styles.salesCardExtra}>
        {dropdownGroup}
        <div className={styles.salesTypeRadio}>
        </div>
      </div>
    }
  >
    <div>
      <Pie
        hasLegend
        subTitle={<FormattedMessage id="dashboardanalysis.analysis.sales" defaultMessage="Sales" />}
        total={() => `${salesPieData.reduce((pre, now) => now.y + pre, 0)}台`}
        data={salesPieData}
        valueFormat={value => `${value}台`}
        height={248}
        lineWidth={4}
      />
    </div>
  </Card>
);

export default ProportionSales;
