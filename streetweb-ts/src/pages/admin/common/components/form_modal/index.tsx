import React, {Component, cloneElement, ReactElement, createRef } from 'react';

import { Modal, Form, Input, Upload, message } from 'antd';

import { merge } from 'lodash';

import { FormInstance, FormItemProps } from 'antd/lib/form';

export type OnCreated<Resource> = (res: Resource) => void;

export type CreateProps<Resource> = {
  type: 'create',
  onCreated?: OnCreated<Resource>;
}

export type OnUpdated<Resource> = (res: Resource) => void;

export type UpdateProps<Resource, FormItems, Id=number> = {
  type: 'update',
  default: FormItems;
  onUpdated?: OnUpdated<Resource>;
}

type Props<Resource, FormItems, Id> = (CreateProps<Resource> | UpdateProps<Resource, FormItems, Id>) & {
  children?: ReactElement,
  id?: Id,
};

export default class<Resource, FormItems, Id=number> extends Component<Props<Resource, FormItems, Id>, {
  visible: boolean,
  loading: boolean,
}> {

  static defaultProps = {
    type: 'create'
  }

  readonly state = {
    visible: false,
    loading: false,
  };

  formRef = createRef<FormInstance>();

  handleForm = async() => {
    try {
      const { props, actionName, onCreating, onUpdating, resTypeName } = this;
      const value = await this.formRef.current!.validateFields() as FormItems & {name?: string};
      try {
        this.setState({
          loading: true,
        })
        switch(props.type) {
          case 'create':
            const resCreated = await onCreating(value, props.id!);
            props.onCreated?.(resCreated);
            break;
          case 'update':
            const resUpdated = await onUpdating(value, props.id!);
            props.onUpdated?.(resUpdated);
            break;
        }
        this.setState({
          visible: false,
        });
        message.success(`${value.name ?? resTypeName}${actionName}成功`);
      } catch {
        message.error(`${value.name ?? resTypeName}${actionName}失败`);
      } finally {
        this.setState({
          loading: false,
        })
      }

    } catch { } 
  }

  render() {
    const { props, actionName, resTypeName, itemsMeta } = this;
    const { children } = this.props;
    const { visible, loading } = this.state;

    let def: Partial<FormItems> | null = props.type == "update" ? props.default : null;
    return (
      <>
        {
          children && cloneElement(children, {
            onClick: () => {
              this.setState({
                visible: true,
              });
              this.formRef.current?.resetFields();
            }
          })
        }
        <Modal
          className='modal'
          title={`${actionName}${resTypeName}`}
          visible={visible}
          confirmLoading={loading}
          //onOk={this.handleForm}
          onCancel={() => {
            this.setState({
              visible: false,
            });
          }}
          onOk={this.handleForm}
          okText={actionName}
          cancelText='取消'
        >
          <Form
            ref={this.formRef}
            labelCol={{span: 6}}
            wrapperCol={{span: 18}}
            initialValues={def!}
          >
            {Object.entries<Omit<FormItemProps, 'name'>>(itemsMeta).map(([k, v]) => (
              <Form.Item name={k} {
                ...merge({
                  rules: [{
                    required: true,
                    message: `请输入${v.label}`,
                  }],
                }, v)
              } />
            ))}
          </Form>
        </Modal>
      </>
    )
  }

  get actionName() {
    return {
      create: '创建',
      update: '更新',
    }[this.props.type];
  }

  get resTypeName(): string {
    throw new Error('not implement');
  }

  get itemsMeta(): Record<keyof FormItems, Omit<FormItemProps, 'name'>> {
    throw new Error('not implement');
  }

  async onCreating(form: FormItems, id: Id): Promise<Resource> {
    throw new Error('not implement');
  }

  async onUpdating(form: FormItems, id: Id): Promise<Resource> {
    throw new Error('not implement');
  }
};
